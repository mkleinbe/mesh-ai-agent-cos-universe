import http from 'node:http';
export declare function nativeSlackHitlConfigured(env?: NodeJS.ProcessEnv): boolean;
export declare function startRemote(env?: NodeJS.ProcessEnv): Promise<http.Server<typeof http.IncomingMessage, typeof http.ServerResponse>>;
