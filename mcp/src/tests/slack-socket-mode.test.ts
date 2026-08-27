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
  fail(): void { this.onerror?.(); }
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

async function tick(): Promise<void> {
  await new Promise(resolve => setImmediate(resolve));
}

function messageEnvelope(id = 'env-1'): Record<string, unknown> {
  return {
    envelope_id: id,
    type: 'events_api',
    payload: {
      type: 'event_callback',
      event_id: `Ev-${id}`,
      event: {
        type: 'message',
        channel: 'C0TEST',
        user: 'U0TEST',
        text: 'APPROVE',
        thread_ts: '1787843216.789639',
        ts: '1787843300.046169',
      },
    },
  };
}

test('Socket Mode app token is protected and must be an app-level xapp token', () => {
  const good = tempSecret('xapp-test-token\n');
  assert.equal(readSlackSocketAppToken(env(good)), 'xapp-test-token');

  const bad = tempSecret('xoxb-wrong-token-type\n');
  assert.throws(() => readSlackSocketAppToken(env(bad)), /app-level token/);
  assert.throws(() => readSlackSocketAppToken({}), /APP_TOKEN_FILE/);
});

test('listener authenticates to apps.connections.open and dispatches Events API envelopes', async () => {
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

  await listener.start();
  await tick();
  socket.open();
  assert.equal(authHeader, 'Bearer xapp-test-token');
  assert.equal(listener.isActive(), true);

  socket.message({ type: 'hello' });
  socket.message({ envelope_id: 'noise', type: 'slash_commands', payload: {} });
  await tick();
  assert.equal(bridged.length, 0);

  const envelope = messageEnvelope();
  socket.message(envelope);
  await tick();
  assert.deepEqual(bridged, [envelope]);
  assert.deepEqual(JSON.parse(socket.sent.at(-1) ?? '{}'), { envelope_id: 'env-1' });
  await listener.stop();
});

test('structured authorization rejection is acknowledged without exposing internals', async () => {
  const socket = new FakeSocket();
  const tokenFile = tempSecret('xapp-test-token');
  const listener = new SlackSocketModeApprovalListener(env(tokenFile), {
    fetchImpl: async () => ({ ok: true, json: async () => ({ ok: true, url: 'wss://socket.test/link' }) }) as Response,
    socketFactory: () => socket,
    bridge: async () => ({ ok: false, error: { type: 'PermissionError' } }),
  });
  await listener.start();
  await tick();
  socket.open();

  socket.message(messageEnvelope('env-rejected'));
  await tick();
  assert.deepEqual(JSON.parse(socket.sent.at(-1) ?? '{}'), { envelope_id: 'env-rejected' });
  assert.equal(socket.sent.some(value => value.includes('PermissionError')), false);
  await listener.stop();
});

test('bridge transport failure is not acknowledged and listener degrades on disconnect', async () => {
  const socket = new FakeSocket();
  const tokenFile = tempSecret('xapp-test-token');
  const listener = new SlackSocketModeApprovalListener(env(tokenFile), {
    fetchImpl: async () => ({ ok: true, json: async () => ({ ok: true, url: 'wss://socket.test/link' }) }) as Response,
    socketFactory: () => socket,
    bridge: async () => { throw new Error('sensitive internal failure'); },
    scheduleReconnect: () => undefined,
  });
  await listener.start();
  await tick();
  socket.open();

  socket.message(messageEnvelope('env-fail'));
  await tick();
  assert.equal(socket.sent.length, 0);

  socket.close();
  assert.equal(listener.isActive(), false);
  await listener.stop();
});

test('provider network failure is non-fatal and reconnect backoff is bounded', async () => {
  const tokenFile = tempSecret('xapp-test-token');
  const scheduled: Array<{ callback: () => void; delayMs: number }> = [];
  let attempts = 0;
  const listener = new SlackSocketModeApprovalListener(env(tokenFile), {
    fetchImpl: async () => {
      attempts += 1;
      throw new Error('simulated provider network failure');
    },
    socketFactory: () => { throw new Error('socket must not be created'); },
    bridge: async () => { throw new Error('bridge must not be called'); },
    scheduleReconnect: (callback, delayMs) => {
      scheduled.push({ callback, delayMs });
      return scheduled.length;
    },
  });

  await listener.start();
  await tick();
  assert.equal(listener.isActive(), false);
  assert.equal(attempts, 1);
  assert.deepEqual(scheduled.map(item => item.delayMs), [1_000]);

  for (let index = 0; index < 7; index += 1) {
    const next = scheduled[index];
    assert.ok(next);
    next.callback();
    await tick();
  }
  assert.ok(scheduled.length >= 8);
  assert.deepEqual(scheduled.slice(0, 6).map(item => item.delayMs), [1_000, 2_000, 4_000, 8_000, 16_000, 30_000]);
  assert.equal(Math.max(...scheduled.map(item => item.delayMs)), 30_000);
  assert.equal(listener.isActive(), false);
  await listener.stop();
});

test('required Socket Mode configuration errors remain fatal before background connection', async () => {
  const listener = new SlackSocketModeApprovalListener(
    { MESH_COS_SLACK_HITL_REQUIRED: 'true' },
    {
      fetchImpl: async () => { throw new Error('must not connect without a credential'); },
      socketFactory: () => { throw new Error('must not connect without a credential'); },
      bridge: async () => { throw new Error('must not bridge'); },
    },
  );
  await assert.rejects(listener.start(), /APP_TOKEN_FILE/);
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
