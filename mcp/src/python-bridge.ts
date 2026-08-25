import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(moduleDir, '../..');
const MAX_RESPONSE_BYTES = 2_000_000;
const DEFAULT_TIMEOUT_MS = 30_000;
const DEFAULT_MAX_QUEUE = 32;
const MAX_ERROR_DETAILS = 32;
const MAX_DETAIL_LENGTH = 160;
let tail: Promise<void> = Promise.resolve();
let queued = 0;

export type BridgeRequest = { tool_name: string; arguments: Record<string, unknown> };
export type SafeErrorDetail = { field: string; reason: string };
export type BridgeResponse = {
  ok: boolean;
  runtime_version?: string;
  agent_id?: string;
  tool_name?: string;
  result?: unknown;
  error?: string;
  error_type?: string;
  details?: unknown;
};

function sanitizeErrorDetails(value: unknown): SafeErrorDetail[] | undefined {
  if (!Array.isArray(value)) return undefined;
  const details: SafeErrorDetail[] = [];
  for (const item of value.slice(0, MAX_ERROR_DETAILS)) {
    if (typeof item !== 'object' || item === null || Array.isArray(item)) continue;
    const record = item as Record<string, unknown>;
    if (typeof record.field !== 'string' || typeof record.reason !== 'string') continue;
    details.push({
      field: record.field.slice(0, MAX_DETAIL_LENGTH),
      reason: record.reason.slice(0, MAX_DETAIL_LENGTH),
    });
  }
  return details.length ? details : undefined;
}

export class PythonBridgeError extends Error {
  readonly category: string;
  readonly details?: SafeErrorDetail[];

  constructor(category: string, details?: unknown) {
    super(`Python bridge failed: ${category}`);
    this.name = 'PythonBridgeError';
    this.category = category;
    this.details = sanitizeErrorDetails(details);
  }
}

export function repositoryRoot(): string { return repoRoot; }

export function pythonEnvironment(env: NodeJS.ProcessEnv = process.env): NodeJS.ProcessEnv {
  const sourcePath = path.join(repoRoot, 'src');
  const existing = env.PYTHONPATH?.trim();
  return { ...env, PYTHONPATH: existing ? `${sourcePath}${path.delimiter}${existing}` : sourcePath };
}

function positiveInt(raw: string | undefined, fallback: number): number {
  const value = Number(raw);
  return Number.isInteger(value) && value > 0 ? value : fallback;
}

async function invokePython(request: BridgeRequest, env: NodeJS.ProcessEnv): Promise<BridgeResponse> {
  const python = env.MESH_COS_PYTHON_BIN?.trim() || 'python';
  const timeoutMs = positiveInt(env.MESH_COS_BRIDGE_TIMEOUT_MS, DEFAULT_TIMEOUT_MS);
  const child = spawn(python, ['-m', 'mesh_cos.mcp_stdio_bridge'], {
    cwd: repoRoot,
    env: pythonEnvironment(env),
    stdio: ['pipe', 'pipe', 'ignore'],
  });
  let stdout = '';
  let outputTooLarge = false;
  let timedOut = false;
  child.stdout.setEncoding('utf8');
  child.stdout.on('data', (chunk: string) => {
    if (Buffer.byteLength(stdout + chunk, 'utf8') > MAX_RESPONSE_BYTES) {
      outputTooLarge = true;
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
  child.stdin.end(JSON.stringify(request));
  let code: number;
  try {
    code = await completed;
  } catch {
    clearTimeout(timer);
    throw new PythonBridgeError('bridge_unavailable');
  }
  clearTimeout(timer);
  if (timedOut) throw new PythonBridgeError('bridge_timeout');
  if (outputTooLarge) throw new PythonBridgeError('response_too_large');
  if (code !== 0) throw new PythonBridgeError('bridge_process_failed');
  let response: BridgeResponse;
  try {
    response = JSON.parse(stdout) as BridgeResponse;
  } catch {
    throw new PythonBridgeError('invalid_bridge_response');
  }
  if (response.ok !== true) {
    throw new PythonBridgeError(response.error || 'execution_failed', response.details);
  }
  return response;
}

export async function callPythonBridge(
  request: BridgeRequest,
  env: NodeJS.ProcessEnv = process.env,
): Promise<BridgeResponse> {
  const maxQueue = positiveInt(env.MESH_COS_MAX_BRIDGE_QUEUE, DEFAULT_MAX_QUEUE);
  if (queued >= maxQueue) throw new PythonBridgeError('bridge_busy');
  queued += 1;
  let release!: () => void;
  const previous = tail;
  tail = new Promise<void>(resolve => { release = resolve; });
  await previous;
  try {
    return await invokePython(request, env);
  } finally {
    queued -= 1;
    release();
  }
}
