export type BridgeRequest = {
    tool_name: string;
    arguments: Record<string, unknown>;
};
export type SafeErrorDetail = {
    field: string;
    reason: string;
};
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
export declare class PythonBridgeError extends Error {
    readonly category: string;
    readonly details?: SafeErrorDetail[];
    constructor(category: string, details?: unknown);
}
export declare function repositoryRoot(): string;
export declare function pythonEnvironment(env?: NodeJS.ProcessEnv): NodeJS.ProcessEnv;
export declare function callPythonBridge(request: BridgeRequest, env?: NodeJS.ProcessEnv): Promise<BridgeResponse>;
