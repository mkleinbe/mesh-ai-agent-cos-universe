import assert from 'node:assert/strict';
import test from 'node:test';
import {
  MAX_ARGUMENT_BYTES,
  createServer,
  loadContract,
  requireAgentId,
  requireDeploymentRelease,
  requireLocalStdioContract,
  safeErrorPayload,
  toolsForAgent,
  validateArgumentsSize,
} from '../server.js';
import { PythonBridgeError, pythonEnvironment, repositoryRoot } from '../python-bridge.js';

const contract = loadContract();

test('contract loads local stdio release metadata', () => {
  assert.equal(contract.name, 'mesh-cos-mcp');
  assert.equal(contract.runtime_release, '4.0.0');
  assert.equal(contract.transport, 'LOCAL_STDIO');
  assert.doesNotThrow(() => requireLocalStdioContract(contract));
  assert.throws(() => requireLocalStdioContract({ ...contract, transport: 'REMOTE_HTTPS' }), /LOCAL_STDIO/);
});

test('agent identity is required and must be registered', () => {
  assert.throws(() => requireAgentId(contract, {}), /MESH_COS_AGENT_ID/);
  assert.throws(() => requireAgentId(contract, { MESH_COS_AGENT_ID: 'unknown' }), /registered/);
  assert.throws(() => requireAgentId(contract, { MESH_COS_AGENT_ID: 'devils-advocate' }), /registered/);
  assert.equal(requireAgentId(contract, { MESH_COS_AGENT_ID: 'message-ops' }), 'message-ops');
  assert.equal(requireAgentId(contract, { MESH_COS_AGENT_ID: 'cro' }), 'cro');
});

test('production deployment release identity is required and normalized', () => {
  assert.throws(() => requireDeploymentRelease({}), /MESH_COS_DEPLOYMENT_RELEASE/);
  assert.throws(() => requireDeploymentRelease({ MESH_COS_DEPLOYMENT_RELEASE: '   ' }), /MESH_COS_DEPLOYMENT_RELEASE/);
  assert.equal(requireDeploymentRelease({ MESH_COS_DEPLOYMENT_RELEASE: ' 4.1.6 ' }), '4.1.6');
});

test('tool projection is exact and excludes human-only tools', () => {
  const humanOnly = new Set(contract.human_tool_allowlist);
  for (const agentId of Object.keys(contract.agent_tool_allowlists)) {
    const projected = toolsForAgent(contract, agentId).map((tool) => tool.name);
    assert.deepEqual(projected, contract.agent_tool_allowlists[agentId]);
    for (const tool of projected) assert.equal(humanOnly.has(tool), false, `${agentId} unexpectedly exposes human-only tool ${tool}`);
  }
  assert.deepEqual(toolsForAgent(contract, 'message-ops').map((tool) => tool.name), contract.agent_tool_allowlists['message-ops']);
  assert.deepEqual(toolsForAgent(contract, 'devils-advocate'), []);
});

test('argument validation is object-only and size bounded', () => {
  assert.deepEqual(validateArgumentsSize(undefined), {});
  assert.deepEqual(validateArgumentsSize({ value: 1 }), { value: 1 });
  assert.throws(() => validateArgumentsSize([]), /object/);
  assert.throws(() => validateArgumentsSize({ value: 'x'.repeat(MAX_ARGUMENT_BYTES + 1) }), /maximum size/);
});

test('safe errors never return raw bridge error messages', () => {
  const bridge = safeErrorPayload(new PythonBridgeError('permission_denied'), 'r1');
  assert.deepEqual(bridge, { ok: false, request_id: 'r1', error: 'permission_denied' });
  assert.equal(JSON.stringify(bridge).includes('secret'), false);
  assert.equal(safeErrorPayload(new Error('Tool arguments exceed maximum size'), 'r2').error, 'request_too_large');
  assert.equal(safeErrorPayload(new Error('Tool arguments must be an object'), 'r3').error, 'invalid_request');
  assert.equal(safeErrorPayload(new Error('unexpected secret'), 'r4').error, 'runtime_error');
});

test('python environment always makes repository src importable', () => {
  const root = repositoryRoot();
  const fresh = pythonEnvironment({});
  assert.equal(fresh.PYTHONPATH, `${root}/src`);
  const existing = pythonEnvironment({ PYTHONPATH: '/existing' });
  assert.ok(existing.PYTHONPATH?.includes('/existing'));
  assert.ok(existing.PYTHONPATH?.includes(`${root}/src`));
});

test('server factory is transport-neutral while stdio entrypoint remains strict', () => {
  const drifted = { ...contract, transport: 'REMOTE_HTTPS' };
  assert.ok(createServer({ MESH_COS_AGENT_ID: 'cos' }, drifted));
  assert.ok(createServer({ MESH_COS_AGENT_ID: 'cos' }, contract));
  assert.ok(createServer({ MESH_COS_AGENT_ID: 'message-ops' }, contract));
});
