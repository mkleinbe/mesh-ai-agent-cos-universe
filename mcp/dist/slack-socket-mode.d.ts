export type SocketLike = {
    onopen: (() => void) | null;
    onmessage: ((event: {
        data: unknown;
    }) => void) | null;
    onerror: (() => void) | null;
    onclose: (() => void) | null;
    send(data: string): void;
    close(): void;
};
type FetchResponse = {
    ok: boolean;
    json(): Promise<unknown>;
};
type FetchLike = (url: string, init?: {
    method?: string;
    headers?: Record<string, string>;
}) => Promise<FetchResponse>;
type SocketFactory = (url: string) => SocketLike;
type Bridge = (envelope: Record<string, unknown>) => Promise<Record<string, unknown>>;
type ReconnectScheduler = (callback: () => void, delayMs: number) => unknown;
type ListenerDependencies = {
    fetchImpl?: FetchLike;
    socketFactory?: SocketFactory;
    bridge?: Bridge;
    scheduleReconnect?: ReconnectScheduler;
};
export declare function readSlackSocketAppToken(env?: NodeJS.ProcessEnv): string;
export declare function callSlackSocketApprovalBridge(envelope: Record<string, unknown>, env?: NodeJS.ProcessEnv): Promise<Record<string, unknown>>;
export declare class SlackSocketModeApprovalListener {
    private readonly env;
    private readonly fetchImpl;
    private readonly socketFactory;
    private readonly bridge;
    private readonly scheduleReconnect;
    private socket;
    private active;
    private stopped;
    private reconnectAttempt;
    private reconnectScheduled;
    constructor(env?: NodeJS.ProcessEnv, dependencies?: ListenerDependencies);
    isRequired(): boolean;
    isActive(): boolean;
    start(): Promise<void>;
    stop(): Promise<void>;
    private reconnectDelayMs;
    private scheduleReconnectAttempt;
    private openUrl;
    private connect;
    private handleMessage;
}
export {};
