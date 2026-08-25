import assert from 'node:assert/strict';
import test from 'node:test';
import {
  loadContract,
  loadInputSchemas,
  requireAgentId,
  safeErrorPayload,
  toolInputSchema,
  toolsForAgent,
} from '../server.js';
import { PythonBridgeError } from '../python-bridge.js';

const contract = loadContract();

test('tool-input schema registry is exact, closed, and projected for every MCP tool', () => {
  const schemas = loadInputSchemas(contract);
  const names = new Set(contract.tools.map((tool) => tool.name));
  assert.deepEqual(new Set(Object.keys(schemas)), names);
  for (const name of names) {
    const schema = toolInputSchema(schemas, name);
    assert.equal(schema.type, 'object');
    assert.equal(schema.additionalProperties, false);
  }
  const intake = toolInputSchema(schemas, 'task.intake');
  assert.ok(Array.isArray(intake.required));
  assert.ok((intake.required as string[]).includes('accountable_agent'));
  const decompose = toolInputSchema(schemas, 'task.decompose');
  assert.ok((decompose.required as string[]).includes('parent_task_id'));
});

test('validation details from the Python boundary are preserved without raw exception text', () => {
  const error = new PythonBridgeError('validation_failed', [
    { field: 'accountable_agent', reason: 'required' },
  ]);
  assert.deepEqual(safeErrorPayload(error, 'req-1'), {
    ok: false,
    request_id: 'req-1',
    error: 'validation_failed',
    details: [{ field: 'accountable_agent', reason: 'required' }],
  });
});

test('all ten registered agent processes receive their exact allowlist and cannot select identity from payload', () => {
  const agents = Object.keys(contract.agent_tool_allowlists);
  assert.equal(agents.length, 10);
  for (const agentId of agents) {
    assert.equal(requireAgentId(contract, { MESH_COS_AGENT_ID: agentId }), agentId);
    assert.deepEqual(
      toolsForAgent(contract, agentId).map((tool) => tool.name),
      contract.agent_tool_allowlists[agentId],
    );
    assert.equal(contract.agent_tool_allowlists[agentId].includes('approval.record_decision'), false);
    assert.equal(contract.agent_tool_allowlists[agentId].includes('reliability.human_override'), false);
  }
});
