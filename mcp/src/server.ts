import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { Server } from '@modelcontextprotocol/server';
import { callPythonBridge, PythonBridgeError, repositoryRoot } from './python-bridge.js';

export const MAX_ARGUMENT_BYTES = 1_000_000;
export type ToolContract = { name: string; description?: string; read_only?: boolean };
export type JsonSchemaValue =
  | string
  | number
  | boolean
  | null
  | JsonSchemaValue[]
  | { [key: string]: JsonSchemaValue };
export type ToolInputSchema = {
  type: 'object';
  properties: Record<string, JsonSchemaValue>;
  required: string[];
  additionalProperties: false;
};
export type InputSchemaRegistry = Record<string, ToolInputSchema>;
export type MCPContract = {
  name: string;
  runtime_release: string;
  transport: string;
  input_schema_registry?: string;
  tools: ToolContract[];
  agent_tool_allowlists: Record<string, string[]>;
  human_tool_allowlist: string[];
};

export function loadContract(): MCPContract {
  return JSON.parse(
    fs.readFileSync(path.join(repositoryRoot(), 'chatgpt', 'mcp', 'mesh-cos-mcp.v1.json'), 'utf8'),
  ) as MCPContract;
}

function schemaTools(payload: Record<string, unknown>, expectedVersion: string): Record<string, unknown> {
  if (payload.schema_version !== expectedVersion) {
    throw new Error(`Unsupported MCP input-schema registry version: ${String(payload.schema_version)}`);
  }
  if (typeof payload.tools !== 'object' || payload.tools === null || Array.isArray(payload.tools)) {
    throw new Error('MCP input-schema registry must contain tools');
  }
  return payload.tools as Record<string, unknown>;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function deepMergeSchema(base: Record<string, unknown>, patch: Record<string, unknown>): Record<string, unknown> {
  const merged: Record<string, unknown> = { ...base };
  for (const [key, value] of Object.entries(patch)) {
    const current = merged[key];
    merged[key] = isRecord(current) && isRecord(value)
      ? deepMergeSchema(current, value)
      : value;
  }
  return merged;
}

function applySchemaPatches(raw: Record<string, unknown>): void {
  const patchPath = path.resolve(repositoryRoot(), 'chatgpt/mcp/tool-input-schema-patches.v1.json');
  if (!fs.existsSync(patchPath)) return;
  const payload = JSON.parse(fs.readFileSync(patchPath, 'utf8')) as Record<string, unknown>;
  const patches = schemaTools(payload, 'mesh.cos.mcp-tool-input-schema-patches.v1');
  for (const [name, patchValue] of Object.entries(patches)) {
    if (!(name in raw)) throw new Error(`MCP input-schema patch references unknown tool: ${name}`);
    if (!isRecord(raw[name]) || !isRecord(patchValue)) {
      throw new Error(`Invalid MCP input-schema patch for ${name}`);
    }
    raw[name] = deepMergeSchema(raw[name] as Record<string, unknown>, patchValue);
  }
}

export function loadInputSchemas(contract: MCPContract = loadContract()): InputSchemaRegistry {
  const target = path.resolve(repositoryRoot(), contract.input_schema_registry ?? 'chatgpt/mcp/tool-input-schemas.v1.json');
  const payload = JSON.parse(fs.readFileSync(target, 'utf8')) as Record<string, unknown>;
  const raw: Record<string, unknown> = {
    ...schemaTools(payload, 'mesh.cos.mcp-tool-input-schemas.v1'),
  };
  const extensionPath = path.resolve(repositoryRoot(), 'chatgpt/mcp/tool-input-schemas.owner-execution.v1.json');
  if (fs.existsSync(extensionPath)) {
    const extension = JSON.parse(fs.readFileSync(extensionPath, 'utf8')) as Record<string, unknown>;
    const extensionTools = schemaTools(extension, 'mesh.cos.mcp-tool-input-schema-extension.v1');
    for (const [name, schema] of Object.entries(extensionTools)) {
      if (name in raw) throw new Error(`MCP input-schema extension duplicates tool: ${name}`);
      raw[name] = schema;
    }
  }
  applySchemaPatches(raw);
  const expected = new Set(contract.tools.map(tool => tool.name));
  if (Object.keys(raw).length !== expected.size || Object.keys(raw).some(name => !expected.has(name))) {
    throw new Error('MCP input-schema registry must exactly match the tool catalog');
  }
  const schemas: InputSchemaRegistry = {};
  for (const [name, schemaValue] of Object.entries(raw)) {
    if (typeof schemaValue !== 'object' || schemaValue === null || Array.isArray(schemaValue)) {
      throw new Error(`Invalid MCP input schema for ${name}`);
    }
    const schema = schemaValue as Record<string, unknown>;
    if (schema.type !== 'object' || schema.additionalProperties !== false) {
      throw new Error(`MCP input schema must be a closed object: ${name}`);
    }
    schemas[name] = schema as ToolInputSchema;
  }
  return schemas;
}

export function toolInputSchema(schemas: InputSchemaRegistry, name: string): ToolInputSchema {
  const schema = schemas[name];
  if (!schema) throw new Error(`Missing MCP input schema for ${name}`);
  return schema;
}

export function requireAgentId(contract: MCPContract, env: NodeJS.ProcessEnv = process.env): string {
  const id = env.MESH_COS_AGENT_ID?.trim();
  if (!id) throw new Error('MESH_COS_AGENT_ID is required');
  if (!(id in contract.agent_tool_allowlists)) {
    throw new Error('MESH_COS_AGENT_ID is not a registered Workspace Agent');
  }
  return id;
}

export function deploymentRelease(env: NodeJS.ProcessEnv = process.env): string | null {
  const value = env.MESH_COS_DEPLOYMENT_RELEASE?.trim();
  return value || null;
}

export function requireDeploymentRelease(env: NodeJS.ProcessEnv = process.env): string {
  const value = deploymentRelease(env);
  if (!value) throw new Error('MESH_COS_DEPLOYMENT_RELEASE is required for remote production runtime');
  return value;
}

export function requireLocalStdioContract(contract: MCPContract): void {
  if (contract.transport !== 'LOCAL_STDIO') throw new Error('Local entrypoint requires LOCAL_STDIO transport');
}

export function toolsForAgent(contract: MCPContract, agentId: string): ToolContract[] {
  const byName = new Map(contract.tools.map(tool => [tool.name, tool]));
  const human = new Set(contract.human_tool_allowlist ?? []);
  return (contract.agent_tool_allowlists[agentId] ?? [])
    .filter(name => !human.has(name))
    .map(name => byName.get(name))
    .filter((tool): tool is ToolContract => tool !== undefined);
}

export function validateArgumentsSize(value: unknown): Record<string, unknown> {
  const args = value ?? {};
  if (typeof args !== 'object' || args === null || Array.isArray(args)) {
    throw new Error('Tool arguments must be an object');
  }
  if (Buffer.byteLength(JSON.stringify(args), 'utf8') > MAX_ARGUMENT_BYTES) {
    throw new Error('Tool arguments exceed maximum size');
  }
  return args as Record<string, unknown>;
}

export function safeErrorPayload(error: unknown, requestId: string): Record<string, unknown> {
  if (error instanceof PythonBridgeError) {
    const payload: Record<string, unknown> = { ok: false, request_id: requestId, error: error.category };
    if (error.category === 'validation_failed' && error.details?.length) payload.details = error.details;
    return payload;
  }
  if (error instanceof Error && error.message.includes('maximum size')) {
    return { ok: false, request_id: requestId, error: 'request_too_large' };
  }
  if (error instanceof Error && error.message.includes('arguments')) {
    return { ok: false, request_id: requestId, error: 'invalid_request' };
  }
  if (error instanceof Error && error.message.includes('not allowed for the bound agent')) {
    return { ok: false, request_id: requestId, error: 'forbidden' };
  }
  return { ok: false, request_id: requestId, error: 'execution_failed' };
}

function logToolEvent(event: Record<string, unknown>): void {
  process.stderr.write(`${JSON.stringify(event)}\n`);
}

export function createServer(
  env: NodeJS.ProcessEnv = process.env,
  contract: MCPContract = loadContract(),
): Server {
  const agentId = requireAgentId(contract, env);
  const deploymentReleaseId = deploymentRelease(env);
  const tools = toolsForAgent(contract, agentId);
  const names = new Set(tools.map(tool => tool.name));
  const inputSchemas = loadInputSchemas(contract);
  const server = new Server(
    { name: contract.name, version: contract.runtime_release },
    { capabilities: { tools: {} } },
  );
  server.setRequestHandler('tools/list', async () => ({
    tools: tools.map(tool => ({
      name: tool.name,
      description: tool.description ?? tool.name,
      inputSchema: toolInputSchema(inputSchemas, tool.name),
    })),
  }));
  server.setRequestHandler('tools/call', async request => {
    const requestId = randomUUID();
    const started = Date.now();
    const toolName = request.params.name;
    try {
      if (!names.has(toolName)) throw new Error('Tool is not allowed for the bound agent');
      const args = validateArgumentsSize(request.params.arguments);
      const response = await callPythonBridge({ tool_name: toolName, arguments: args }, env);
      logToolEvent({
        event: 'mcp_tool', request_id: requestId, agent_id: agentId, tool_name: toolName,
        result_classification: 'success', latency_ms: Date.now() - started,
      });
      return {
        content: [{
          type: 'text' as const,
          text: JSON.stringify({
            ok: true,
            request_id: requestId,
            mcp_version: contract.runtime_release,
            deployment_release: deploymentReleaseId,
            agent_id: agentId,
            result: response.result,
          }),
        }],
      };
    } catch (error) {
      const safe = safeErrorPayload(error, requestId);
      logToolEvent({
        event: 'mcp_tool', request_id: requestId, agent_id: agentId, tool_name: toolName,
        result_classification: safe.error, latency_ms: Date.now() - started,
      });
      return {
        isError: true,
        content: [{
          type: 'text' as const,
          text: JSON.stringify({
            ...safe,
            mcp_version: contract.runtime_release,
            deployment_release: deploymentReleaseId,
            agent_id: agentId,
          }),
        }],
      };
    }
  });
  return server;
}
