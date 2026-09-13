import { Server } from '@modelcontextprotocol/server';
export declare const MAX_ARGUMENT_BYTES = 1000000;
export type ToolContract = {
    name: string;
    description?: string;
    read_only?: boolean;
};
export type JsonSchemaValue = string | number | boolean | null | JsonSchemaValue[] | {
    [key: string]: JsonSchemaValue;
};
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
export declare function loadContract(): MCPContract;
export declare function loadInputSchemas(contract?: MCPContract): InputSchemaRegistry;
export declare function toolInputSchema(schemas: InputSchemaRegistry, name: string): ToolInputSchema;
export declare function requireAgentId(contract: MCPContract, env?: NodeJS.ProcessEnv): string;
export declare function deploymentRelease(env?: NodeJS.ProcessEnv): string | null;
export declare function sourceCommit(env?: NodeJS.ProcessEnv): string | null;
export declare function requireDeploymentRelease(env?: NodeJS.ProcessEnv): string;
export declare function requireLocalStdioContract(contract: MCPContract): void;
export declare function toolsForAgent(contract: MCPContract, agentId: string): ToolContract[];
export declare function actionSchemaDigest(contract: MCPContract, schemas: InputSchemaRegistry, agentId: string): string;
export declare function validateArgumentsSize(value: unknown): Record<string, unknown>;
export declare function safeErrorPayload(error: unknown, requestId: string): Record<string, unknown>;
export declare function createServer(env?: NodeJS.ProcessEnv, contract?: MCPContract): Server;
