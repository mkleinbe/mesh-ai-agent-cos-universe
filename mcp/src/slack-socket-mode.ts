import { spawn } from 'node:child_process';
import fs from 'node:fs';

import { pythonEnvironment, repositoryRoot } from './python-bridge.js';

const CONNECTIONS_OPEN_URL = 'https://slack.com/api/apps.connections.open';
const DEFAULT_CONNECT_TIMEOUT_MS = 10_000;
const DEFAULT_BRIDGE_TIMEOUT_MS = 5_000;
const MAX_BRIDGE_RESPONSE_BYTES = 1_000_000;

export type SocketLike = {
  onopen: (() => void) | null;
  onmessage: ((event: { data: unknown }) => void) | null;
  onerror: (() => void) | null;
  onclose: (() => void) | null;
  send(data: string): void;
  close(): void;
};

type FetchResponse = { ok: boolean; json(): Promise<unknown> };
type FetchLike = (
  url: string,
  init?: { method?: string; headers?: Record<string, string> },
) => Promise<FetchResponse>;
type SocketFactory = (url: string) => SocketLike;
type Bridge = (envelope: Record<string, unknown>) => Promise<Record<string, unknown>>;
type ReconnectScheduler = (callback: () => void, delayMs: number) => unknown;

type ListenerDependencies = {
  fetchImpl?: FetchLike;
  socketFactory?: SocketFactory;
  bridge?: Bridge;
  scheduleReconnect?: ReconnectScheduler;
};

function truthy(value: string | undefined): boolean {
  return ['1', 'true', 'yes', 'on'].includes((value ?? '').trim().toLowerCase());
}

export function readSlackSocketAppToken(env: NodeJS.ProcessEnv = process.env): string {
  const file = env.MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE?.trim();
  if (!file) throw new Error('MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE is required');
  let token: string;
  try {
    token = fs.readFileSync(file, 'utf8').trim();
  } catch {
    throw new Error('Slack Socket Mode app token file is unavailable');
  }
  if (!token.startsWith('xapp-')) throw new Error('Slack Socket Mode requires an app-level token');
  return token;
}

function defaultSocketFactory(url: string): SocketLike {
  const constructor = (globalThis as unknown as {
    WebSocket?: new (target: string) => SocketLike;
  }).WebSocket;
  if (!constructor) throw new Error('Node runtime does not provide WebSocket support');
  return new constructor(url);
}

async function defaultFetch(
  url: string,
  init?: { method?: string; headers?: Record<string, string> },
): Promise<FetchResponse> {
  return fetch(url, init);
}

let bridgeTail: Promise<void> = Promise.resolve();

async function invokeTrustedBridge(
  envelope: Record<string, unknown>,
  env: NodeJS.ProcessEnv,
): Promise<Record<string, unknown>> {
  const python = env.MESH_COS_PYTHON_BIN?.trim() || 'python';
  const timeoutValue = Number(env.MESH_COS_SLACK_BRIDGE_TIMEOUT_MS ?? DEFAULT_BRIDGE_TIMEOUT_MS);
  const timeoutMs = Number.isInteger(timeoutValue) && timeoutValue > 0
    ? timeoutValue
    : DEFAULT_BRIDGE_TIMEOUT_MS;
  const child = spawn(python, ['-m', 'mesh_cos.slack_socket_bridge'], {
    cwd: repositoryRoot(),
    env: pythonEnvironment(env),
    stdio: ['pipe', 'pipe', 'ignore'],
  });
  let stdout = '';
  let tooLarge = false;
  let timedOut = false;
  child.stdout.setEncoding('utf8');
  child.stdout.on('data', (chunk: string) => {
    if (Buffer.byteLength(stdout + chunk, 'utf8') > MAX_BRIDGE_RESPONSE_BYTES) {
      tooLarge = true;
      child.kill('SIGKILL');
      return;
    }
    stdout += chunk;
  });
  const timer = setTimeout(() => {
    timedOut = true;
    child.kill('SIGKILL');
  }, timeoutMs);
  const completed = new Promise<number>((resolve, reject) => {
    child.once('error', reject);
    child.once('close', code => resolve(code ?? 1));
  });
  child.stdin.end(JSON.stringify(envelope));
  let code: number;
  try {
    code = await completed;
  } finally {
    clearTimeout(timer);
  }
  if (timedOut) throw new Error('Slack approval bridge timed out');
  if (tooLarge) throw new Error('Slack approval bridge response exceeded maximum size');
  if (code !== 0) throw new Error('Slack approval bridge process failed');
  let response: Record<string, unknown>;
  try {
    response = JSON.parse(stdout) as Record<string, unknown>;
  } catch {
    throw new Error('Slack approval bridge returned invalid JSON');
  }
  if (response.ok !== true) throw new Error('Slack approval bridge rejected the interaction');
  return response;
}

export async function callSlackSocketApprovalBridge(
  envelope: Record<string, unknown>,
  env: NodeJS.ProcessEnv = process.env,
): Promise<Record<string, unknown>> {
  let release!: () => void;
  const previous = bridgeTail;
  bridgeTail = new Promise<void>(resolve => { release = resolve; });
  await previous;
  try {
    return await invokeTrustedBridge(envelope, env);
  } finally {
    release();
  }
}

function textData(value: unknown): string | null {
  if (typeof value === 'string') return value;
  if (Buffer.isBuffer(value)) return value.toString('utf8');
  if (value instanceof ArrayBuffer) return Buffer.from(value).toString('utf8');
  return null;
}

export class SlackSocketModeApprovalListener {
  private readonly env: NodeJS.ProcessEnv;
  private readonly fetchImpl: FetchLike;
  private readonly socketFactory: SocketFactory;
  private readonly bridge: Bridge;
  private readonly scheduleReconnect: ReconnectScheduler;
  private socket: SocketLike | null = null;
  private active = false;
  private stopped = false;

  constructor(env: NodeJS.ProcessEnv = process.env, dependencies: ListenerDependencies = {}) {
    this.env = env;
    this.fetchImpl = dependencies.fetchImpl ?? defaultFetch;
    this.socketFactory = dependencies.socketFactory ?? defaultSocketFactory;
    this.bridge = dependencies.bridge ?? (envelope => callSlackSocketApprovalBridge(envelope, env));
    this.scheduleReconnect = dependencies.scheduleReconnect ?? ((callback, delayMs) => setTimeout(callback, delayMs));
  }

  isRequired(): boolean {
    return truthy(this.env.MESH_COS_SLACK_HITL_REQUIRED);
  }

  isActive(): boolean {
    return !this.isRequired() || this.active;
  }

  async start(): Promise<void> {
    this.stopped = false;
    if (!this.isRequired()) {
      this.active = true;
      return;
    }
    await this.connect(true);
  }

  async stop(): Promise<void> {
    this.stopped = true;
    this.active = false;
    const socket = this.socket;
    this.socket = null;
    socket?.close();
  }

  private async openUrl(): Promise<string> {
    const token = readSlackSocketAppToken(this.env);
    const response = await this.fetchImpl(CONNECTIONS_OPEN_URL, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    if (!response.ok) throw new Error('Slack Socket Mode connection request failed');
    const payload = await response.json();
    if (typeof payload !== 'object' || payload === null || Array.isArray(payload)) {
      throw new Error('Slack Socket Mode connection response is invalid');
    }
    const record = payload as Record<string, unknown>;
    const url = typeof record.url === 'string' ? record.url : '';
    if (record.ok !== true || !url.startsWith('wss://')) {
      throw new Error('Slack Socket Mode connection URL is unavailable');
    }
    return url;
  }

  private async connect(waitForOpen: boolean): Promise<void> {
    if (this.stopped) return;
    const url = await this.openUrl();
    const socket = this.socketFactory(url);
    this.socket = socket;
    this.active = false;

    let resolveOpen: (() => void) | undefined;
    let rejectOpen: ((reason?: unknown) => void) | undefined;
    const opened = new Promise<void>((resolve, reject) => {
      resolveOpen = resolve;
      rejectOpen = reject;
    });
    const connectTimeoutValue = Number(
      this.env.MESH_COS_SLACK_SOCKET_CONNECT_TIMEOUT_MS ?? DEFAULT_CONNECT_TIMEOUT_MS,
    );
    const connectTimeoutMs = Number.isInteger(connectTimeoutValue) && connectTimeoutValue > 0
      ? connectTimeoutValue
      : DEFAULT_CONNECT_TIMEOUT_MS;
    const timer = setTimeout(() => rejectOpen?.(new Error('Slack Socket Mode connect timeout')), connectTimeoutMs);

    socket.onopen = () => {
      clearTimeout(timer);
      this.active = true;
      resolveOpen?.();
    };
    socket.onerror = () => {
      this.active = false;
      rejectOpen?.(new Error('Slack Socket Mode connection failed'));
    };
    socket.onclose = () => {
      clearTimeout(timer);
      this.active = false;
      if (!this.stopped) {
        this.scheduleReconnect(() => {
          void this.connect(false).catch(() => { this.active = false; });
        }, 1_000);
      }
    };
    socket.onmessage = event => {
      void this.handleMessage(event.data);
    };

    if (waitForOpen) await opened;
  }

  private async handleMessage(data: unknown): Promise<void> {
    const raw = textData(data);
    if (!raw) return;
    let envelope: Record<string, unknown>;
    try {
      const parsed = JSON.parse(raw) as unknown;
      if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) return;
      envelope = parsed as Record<string, unknown>;
    } catch {
      return;
    }
    const type = String(envelope.type ?? '');
    if (type === 'hello') {
      this.active = true;
      return;
    }
    if (type === 'disconnect') {
      this.active = false;
      this.socket?.close();
      return;
    }
    if (type !== 'slash_commands') return;
    const envelopeId = typeof envelope.envelope_id === 'string' ? envelope.envelope_id : '';
    if (!envelopeId) return;
    let success = false;
    try {
      await this.bridge(envelope);
      success = true;
    } catch {
      success = false;
    }
    this.socket?.send(JSON.stringify({
      envelope_id: envelopeId,
      payload: { text: success ? 'Approval recorded.' : 'Approval not recorded.' },
    }));
  }
}
