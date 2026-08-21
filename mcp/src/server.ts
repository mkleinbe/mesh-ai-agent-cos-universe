import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { callPythonBridge, PythonBridgeError, repositoryRoot } from './python-bridge.js';

export const MAX_ARGUMENT_BYTES = 1_000_000;

export type ToolContract = {
  name: string;
  description?: string;
  read_only?: boolean;
};

export type MCPContract = {
  name: string;
  runtime_release: string;
  transport: string;
  tools: ToolContract[];
  agent_tool_allowlists: Record<string, string[]>;
  human_tool_allowlist: string[];
};

export function loadContract(): MCPContract {
  const file = path.join(repositoryRoot(), 'chatgpt', 'mcp', 'mesh-cos-mcp.v1.json');
  return JSON.parse(fs.readFileSync(file, 'utf8')) as MCPContract;
}

export function requireAgentId(
  contract: MCPContract,
  env: NodeJS.ProcessEnv = process.env,
): string {
  const agentId = env.MESH_COS_AGENT_ID?.trim();
  if (!agentId) throw new Error('MESH_COS_AGENT_ID is required');
  if (!(agentId in contract.agent_tool_allowlists)) {
    throw new Error('MESH_COS_AGENT_ID is not a registered Workspace Agent');
  }
  return agentId;
}

export function toolsForAgent(contract: MCPContract, agentId: string): ToolContract[] {
  const allowed = new Set(contract.agent_tool_allowlists[agentId] ?? []);
  const humanOnly = new Set(contract.human_tool_allowlist ?? []);
  return contract.tools.filter((tool) => allowed.has(tool.name) && !humanOnly.has(tool.name));
}

export function validateArgumentsSize(argumentsValue: unknown): Record<string, unknown> {
  const value = argumentsValue ?? {};
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new Error('Tool arguments must be an object');
  }
  const serialized = JSON.stringify(value);
  if (Buffer.byteLength(serialized, 'utf8') > MAX_ARGUMENT_BYTES) {
    throw new Error('Tool arguments exceed maximum size');
  }
  return value as Record<string, unknown>;
}

export function safeErrorPayload(error: unknown, requestId: string): Record<string, unknown> {
  const category = error instanceof PythonBridgeError
    ? error.category
    : error instanceof Error && error.message.includes('maximum size')
      ? 'request_too_large'
      : error instanceof Error && error.message.includes('arguments')
        ? 'invalid_request'
        : 'runtime_error';
  return { ok: false, request_id: requestId, error: category };
}

export function createServer(
  env: NodeJS.ProcessEnv = process.env,
  contract: MCPContract = loadContract(),
): Server {
  if (contract.transport !== 'LOCAL_STDIO') {
    throw new Error('mesh-cos-mcp requires LOCAL_STDIO transport');
  }
  const agentId = requireAgentId(contract, env);
  const allowedTools = toolsForAgent(contract, agentId);
  const allowedNames = new Set(allowedTools.map((tool) => tool.name));

  const server = new Server(
    { name: contract.name, version: contract.runtime_release },
    { capabilities: { tools: {} } },
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: allowedTools.map((tool) => ({
      name: tool.name,
      description: tool.description ?? tool.name,
      inputSchema: { type: 'object' as const, additionalProperties: true },
    })),
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const requestId = randomUUID();
    try {
      const toolName = request.params.name;
      if (!allowedNames.has(toolName)) throw new Error('Tool is not allowed for the bound agent');
      const args = validateArgumentsSize(request.params.arguments);
      const response = await callPythonBridge(
        { tool_name: toolName, arguments: args },
        env,
      );
      return {
        content: [{
          type: 'text' as const,
          text: JSON.stringify({
            ok: true,
            request_id: requestId,
            mcp_version: contract.runtime_release,
            agent_id: agentId,
            result: response.result,
          }),
        }],
      };
    } catch (error) {
      return {
        isError: true,
        content: [{
          type: 'text' as const,
          text: JSON.stringify(safeErrorPayload(error, requestId)),
        }],
      };
    }
  });

  return server;
}
