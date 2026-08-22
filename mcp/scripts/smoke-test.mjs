#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const mcpDir = path.resolve(scriptDir, '..');
const repoRoot = path.resolve(mcpDir, '..');
const contract = JSON.parse(fs.readFileSync(path.join(repoRoot, 'chatgpt', 'mcp', 'mesh-cos-mcp.v1.json'), 'utf8'));
const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mesh-cos-mcp-'));
const ledgerPath = path.join(tempDir, 'ledger.sqlite3');
const env = {
  ...process.env,
  MESH_COS_AGENT_ID: 'cos',
  MESH_COS_LEDGER_PATH: ledgerPath,
  MESH_COS_KILL_SWITCH: 'false',
};

const transport = new StdioClientTransport({
  command: process.execPath,
  args: [path.join(mcpDir, 'dist', 'index.js')],
  env,
  stderr: 'pipe',
});
const client = new Client(
  { name: 'mesh-cos-local-smoke', version: contract.runtime_release },
  { capabilities: {} },
);

async function call(name, args = {}) {
  const response = await client.callTool({ name, arguments: args });
  const textItem = response.content.find((item) => item.type === 'text');
  assert.ok(textItem && 'text' in textItem, `Expected text result from ${name}`);
  const payload = JSON.parse(textItem.text);
  assert.notEqual(response.isError, true, `${name} failed: ${textItem.text}`);
  assert.equal(payload.mcp_version, contract.runtime_release);
  assert.equal(payload.agent_id, 'cos');
  assert.ok(payload.request_id);
  return payload.result;
}

try {
  await client.connect(transport);
  const catalog = await client.listTools();
  const names = catalog.tools.map((tool) => tool.name);
  assert.deepEqual(names, contract.agent_tool_allowlists.cos);
  assert.equal(names.includes('approval.record_decision'), false);
  assert.equal(names.includes('reliability.human_override'), false);

  const agents = await call('registry.list_agents');
  assert.equal(agents.length, 10);
  assert.equal(agents.some((agent) => agent.agent_id === 'devils-advocate'), false);
  assert.equal(agents.some((agent) => agent.agent_id === 'message-ops'), true);

  const task = await call('task.intake', {
    objective: 'certify local stdio runtime',
    expected_outcome: 'persistent governed task',
    requested_by: 'michael',
    executive_sponsor: 'michael',
    accountable_agent: 'cos',
    decision_owner: 'michael',
    authority_level: 2,
    acceptance_test: 'task can be read from the same canonical ledger',
    idempotency_key: 'local-mcp-smoke-v4',
  });
  assert.ok(task.task_id);
  const reread = await call('task.get', { task_id: task.task_id });
  assert.equal(reread.task_id, task.task_id);

  const denied = await client.callTool({
    name: 'approval.record_decision',
    arguments: { unexpected_secret: 'do-not-leak' },
  });
  assert.equal(denied.isError, true);
  const deniedText = denied.content.find((item) => item.type === 'text');
  assert.ok(deniedText && 'text' in deniedText);
  assert.equal(deniedText.text.includes('do-not-leak'), false);

  console.log(`CoS MCP stdio certification passed: ${names.length} CoS tools, 10-agent roster, local canonical persistence, human-only exclusion, Devil's Advocate shared-capability principal exclusion, and safe denial behavior.`);
} finally {
  await client.close();
  fs.rmSync(tempDir, { recursive: true, force: true });
}
