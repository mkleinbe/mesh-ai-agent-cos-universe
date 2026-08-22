import assert from 'node:assert/strict';
import test from 'node:test';
import {
  MAX_ARGUMENT_BYTES,
  createServer,
  loadContract,
  requireAgentId,
  safeErrorPayload,
  toolsForAgent,
  validateArgumentsSize,
} from '../server.js';
import { PythonBridgeError, pythonEnvironment, repositoryRoot } from '../python-bridge.js';

const contract = loadContract();

test('contract loads local stdio release metadata', () => {
  assert.equal(contract.name, 'mesh-cos-mcp');
  assert.equal(contract.runtime_release, '3.0.0');
  assert.equal(contract.transport, 'LOCAL_STDIO');
});

test('agent identity is required and must be registered', () => {
  assert.throws(() => requireAgentId(contract, {}), /MESH_COS_AGENT_ID/);
  assert.throws(() => requireAgentId(contract, { MESH_COS_AGENT_ID: 'unknown' }), /registered/);
  assert.throws(() => requireAgentId(contract, { MESH_COS_AGENT_ID: 'message-ops' }), /registered/);
  assert.equal(requireAgentId(contract, { MESH_COS_AGENT_ID: 'cro' }), 'cro');
});

test('tool projection is exact and excludes human-only tools', () => {
  const cos = toolsForAgent(contract, 'cos').map((tool) => tool.name);
  assert.deepEqual(cos, contract.agent_tool_allowlists.cos);
  assert.equal(cos.includes('approval.record_decision'), false);
  assert.equal(cos.includes('reliability.human_override'), false);
  assert.equal(contract.agent_tool_allowlists['message-ops'], undefined);
  assert.deepEqual(toolsForAgent(contract, 'message-ops'), []);
});

test('argument validation is object-only and size bounded', () => {
  assert.deepEqual(validateArgumentsSize(undefined), {});
  assert.deepEqual(validateArgumentsSize({ value: 1 }), { value: 1 });
  assert.throws(() => validateArgumentsSize([]), /object/);
  assert.throws(
    () => validateArgumentsSize({ value: 'x'.repeat(MAX_ARGUMENT_BYTES + 1) }),
    /maximum size/,
  );
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

test('server creation rejects transport drift and accepts a registered agent', () => {
  const drifted = { ...contract, transport: 'REMOTE_HTTPS' };
  assert.throws(() => createServer({ MESH_COS_AGENT_ID: 'cos' }, drifted), /LOCAL_STDIO/);
  assert.ok(createServer({ MESH_COS_AGENT_ID: 'cos' }, contract));
});
