import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

import {
  SlackSocketModeApprovalListener,
  readSlackSocketAppToken,
  type SocketLike,
} from '../slack-socket-mode.js';

class FakeSocket implements SocketLike {
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: unknown }) => void) | null = null;
  onerror: (() => void) | null = null;
  onclose: (() => void) | null = null;
  sent: string[] = [];
  closed = false;

  send(data: string): void { this.sent.push(data); }
  close(): void { this.closed = true; this.onclose?.(); }
  open(): void { this.onopen?.(); }
  message(value: unknown): void { this.onmessage?.({ data: JSON.stringify(value) }); }
}

function tempSecret(value: string): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'mesh-slack-socket-'));
  const file = path.join(dir, 'app-token');
  fs.writeFileSync(file, value, { mode: 0o600 });
  return file;
}

function env(tokenFile: string): NodeJS.ProcessEnv {
  return {
    MESH_COS_SLACK_HITL_REQUIRED: 'true',
    MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE: tokenFile,
  };
}

test('Socket Mode app token is protected and must be an app-level xapp token', () => {
  const good = tempSecret('xapp-test-token\n');
  assert.equal(readSlackSocketAppToken(env(good)), 'xapp-test-token');

  const bad = tempSecret('xoxb-wrong-token-type\n');
  assert.throws(() => readSlackSocketAppToken(env(bad)), /app-level token/);
  assert.throws(() => readSlackSocketAppToken({}), /APP_TOKEN_FILE/);
});

test('listener authenticates to apps.connections.open and dispatches only slash command envelopes', async () => {
  const socket = new FakeSocket();
  const bridged: unknown[] = [];
  const tokenFile = tempSecret('xapp-test-token');
  let authHeader = '';
  const listener = new SlackSocketModeApprovalListener(env(tokenFile), {
    fetchImpl: async (_url, init) => {
      authHeader = String((init?.headers as Record<string, string>)?.Authorization ?? '');
      return {
        ok: true,
        json: async () => ({ ok: true, url: 'wss://socket.test/link' }),
      } as Response;
    },
    socketFactory: () => socket,
    bridge: async envelope => {
      bridged.push(envelope);
      return { ok: true, result: { disposition: 'APPROVE' } };
    },
  });

  const started = listener.start();
  await new Promise(resolve => setImmediate(resolve));
  socket.open();
  await started;
  assert.equal(authHeader, 'Bearer xapp-test-token');
  assert.equal(listener.isActive(), true);

  socket.message({ type: 'hello' });
  socket.message({ envelope_id: 'noise', type: 'events_api', payload: { event: { type: 'message' } } });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(bridged.length, 0);

  const envelope = {
    envelope_id: 'env-1',
    type: 'slash_commands',
    accepts_response_payload: true,
    payload: {
      command: '/mesh-approval',
      text: 'APPROVE approval-test',
      channel_id: 'C0TEST',
      user_id: 'U0TEST',
      trigger_id: 'trigger-1',
    },
  };
  socket.message(envelope);
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(bridged, [envelope]);
  assert.deepEqual(JSON.parse(socket.sent.at(-1) ?? '{}'), {
    envelope_id: 'env-1',
    payload: { text: 'Approval recorded.' },
  });
  await listener.stop();
});

test('listener acknowledges failure without exposing bridge internals and fails readiness on disconnect', async () => {
  const socket = new FakeSocket();
  const tokenFile = tempSecret('xapp-test-token');
  const listener = new SlackSocketModeApprovalListener(env(tokenFile), {
    fetchImpl: async () => ({ ok: true, json: async () => ({ ok: true, url: 'wss://socket.test/link' }) }) as Response,
    socketFactory: () => socket,
    bridge: async () => { throw new Error('sensitive internal failure'); },
    scheduleReconnect: () => undefined,
  });
  const started = listener.start();
  await new Promise(resolve => setImmediate(resolve));
  socket.open();
  await started;

  socket.message({
    envelope_id: 'env-fail',
    type: 'slash_commands',
    accepts_response_payload: true,
    payload: {},
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(JSON.parse(socket.sent.at(-1) ?? '{}'), {
    envelope_id: 'env-fail',
    payload: { text: 'Approval not recorded.' },
  });
  assert.equal(socket.sent.some(value => value.includes('sensitive internal failure')), false);

  socket.close();
  assert.equal(listener.isActive(), false);
  await listener.stop();
});

test('Socket Mode is inert when HITL is not required', async () => {
  const listener = new SlackSocketModeApprovalListener(
    { MESH_COS_SLACK_HITL_REQUIRED: 'false' },
    {
      fetchImpl: async () => { throw new Error('must not connect'); },
      socketFactory: () => { throw new Error('must not connect'); },
      bridge: async () => { throw new Error('must not bridge'); },
    },
  );
  await listener.start();
  assert.equal(listener.isRequired(), false);
  assert.equal(listener.isActive(), true);
  await listener.stop();
});
