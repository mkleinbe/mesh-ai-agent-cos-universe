import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(moduleDir, '../..');
const MAX_RESPONSE_BYTES = 2_000_000;

export type BridgeRequest = {
  tool_name: string;
  arguments: Record<string, unknown>;
};

export type BridgeResponse = {
  ok: boolean;
  runtime_version?: string;
  agent_id?: string;
  tool_name?: string;
  result?: unknown;
  error?: string;
  error_type?: string;
};

export class PythonBridgeError extends Error {
  readonly category: string;

  constructor(category: string) {
    super(`Python bridge failed: ${category}`);
    this.name = 'PythonBridgeError';
    this.category = category;
  }
}

export function repositoryRoot(): string {
  return repoRoot;
}

export function pythonEnvironment(env: NodeJS.ProcessEnv = process.env): NodeJS.ProcessEnv {
  const sourcePath = path.join(repoRoot, 'src');
  const existing = env.PYTHONPATH?.trim();
  return {
    ...env,
    PYTHONPATH: existing ? `${sourcePath}${path.delimiter}${existing}` : sourcePath,
  };
}

export async function callPythonBridge(
  request: BridgeRequest,
  env: NodeJS.ProcessEnv = process.env,
): Promise<BridgeResponse> {
  const python = env.MESH_COS_PYTHON_BIN?.trim() || 'python';
  const child = spawn(python, ['-m', 'mesh_cos.mcp_stdio_bridge'], {
    cwd: repoRoot,
    env: pythonEnvironment(env),
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  let stdout = '';
  let stderr = '';
  let outputTooLarge = false;

  child.stdout.setEncoding('utf8');
  child.stderr.setEncoding('utf8');
  child.stdout.on('data', (chunk: string) => {
    if (stdout.length + chunk.length > MAX_RESPONSE_BYTES) {
      outputTooLarge = true;
      child.kill();
      return;
    }
    stdout += chunk;
  });
  child.stderr.on('data', (chunk: string) => {
    if (stderr.length < 4096) stderr += chunk.slice(0, 4096 - stderr.length);
  });

  const completed = new Promise<number>((resolve, reject) => {
    child.once('error', reject);
    child.once('close', (code) => resolve(code ?? 1));
  });

  child.stdin.end(JSON.stringify(request));
  let code: number;
  try {
    code = await completed;
  } catch {
    throw new PythonBridgeError('bridge_unavailable');
  }
  if (outputTooLarge) throw new PythonBridgeError('response_too_large');
  if (code !== 0) throw new PythonBridgeError(stderr ? 'bridge_process_failed' : 'bridge_process_failed');

  let response: BridgeResponse;
  try {
    response = JSON.parse(stdout) as BridgeResponse;
  } catch {
    throw new PythonBridgeError('invalid_bridge_response');
  }
  if (response.ok !== true) {
    throw new PythonBridgeError(response.error || 'runtime_error');
  }
  return response;
}
