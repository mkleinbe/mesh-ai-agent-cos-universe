import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { Server } from '@modelcontextprotocol/server';
import { callPythonBridge, PythonBridgeError, repositoryRoot } from './python-bridge.js';

export const MAX_ARGUMENT_BYTES = 1_000_000;
export type ToolContract = { name: string; description?: string; read_only?: boolean };
export type MCPContract = { name: string; runtime_release: string; transport: string; tools: ToolContract[]; agent_tool_allowlists: Record<string,string[]>; human_tool_allowlist: string[] };

export function loadContract(): MCPContract {
  return JSON.parse(fs.readFileSync(path.join(repositoryRoot(),'chatgpt','mcp','mesh-cos-mcp.v1.json'),'utf8')) as MCPContract;
}
export function requireAgentId(contract:MCPContract, env:NodeJS.ProcessEnv=process.env):string {
  const id=env.MESH_COS_AGENT_ID?.trim();
  if(!id) throw new Error('MESH_COS_AGENT_ID is required');
  if(!(id in contract.agent_tool_allowlists)) throw new Error('MESH_COS_AGENT_ID is not a registered Workspace Agent');
  return id;
}
export function deploymentRelease(env:NodeJS.ProcessEnv=process.env):string|null {
  const value=env.MESH_COS_DEPLOYMENT_RELEASE?.trim();
  return value||null;
}
export function requireDeploymentRelease(env:NodeJS.ProcessEnv=process.env):string {
  const value=deploymentRelease(env);
  if(!value) throw new Error('MESH_COS_DEPLOYMENT_RELEASE is required for remote production runtime');
  return value;
}
export function requireLocalStdioContract(contract:MCPContract):void {
  if(contract.transport!=='LOCAL_STDIO') throw new Error('Local entrypoint requires LOCAL_STDIO transport');
}
export function toolsForAgent(contract:MCPContract,agentId:string):ToolContract[]{
  const byName=new Map(contract.tools.map(t=>[t.name,t]));
  const human=new Set(contract.human_tool_allowlist??[]);
  return (contract.agent_tool_allowlists[agentId]??[]).filter(n=>!human.has(n)).map(n=>byName.get(n)).filter((t):t is ToolContract=>t!==undefined);
}
export function validateArgumentsSize(v:unknown):Record<string,unknown>{
  const value=v??{};
  if(typeof value!=='object'||value===null||Array.isArray(value)) throw new Error('Tool arguments must be an object');
  if(Buffer.byteLength(JSON.stringify(value),'utf8')>MAX_ARGUMENT_BYTES) throw new Error('Tool arguments exceed maximum size');
  return value as Record<string,unknown>;
}
export function safeErrorPayload(error:unknown,requestId:string):Record<string,unknown>{
  const category=error instanceof PythonBridgeError?error.category:error instanceof Error&&error.message.includes('maximum size')?'request_too_large':error instanceof Error&&error.message.includes('arguments')?'invalid_request':'runtime_error';
  return {ok:false,request_id:requestId,error:category};
}
function logToolEvent(event: Record<string, unknown>): void {
  process.stderr.write(`${JSON.stringify(event)}\n`);
}
export function createServer(env:NodeJS.ProcessEnv=process.env,contract:MCPContract=loadContract()):Server {
  const agentId=requireAgentId(contract,env);
  const deploymentReleaseId=deploymentRelease(env);
  const tools=toolsForAgent(contract,agentId);
  const names=new Set(tools.map(t=>t.name));
  const server=new Server({name:contract.name,version:contract.runtime_release},{capabilities:{tools:{}}});
  server.setRequestHandler('tools/list',async()=>({tools:tools.map(t=>({name:t.name,description:t.description??t.name,inputSchema:{type:'object' as const,additionalProperties:true}}))}));
  server.setRequestHandler('tools/call',async request=>{
    const requestId=randomUUID();
    const started=Date.now();
    const toolName=request.params.name;
    try {
      if(!names.has(toolName)) throw new Error('Tool is not allowed for the bound agent');
      const args=validateArgumentsSize(request.params.arguments);
      const response=await callPythonBridge({tool_name:toolName,arguments:args},env);
      logToolEvent({event:'mcp_tool',request_id:requestId,agent_id:agentId,tool_name:toolName,result_classification:'success',latency_ms:Date.now()-started});
      return {content:[{type:'text' as const,text:JSON.stringify({ok:true,request_id:requestId,mcp_version:contract.runtime_release,deployment_release:deploymentReleaseId,agent_id:agentId,result:response.result})}]};
    } catch(error){
      const safe=safeErrorPayload(error,requestId);
      logToolEvent({event:'mcp_tool',request_id:requestId,agent_id:agentId,tool_name:toolName,result_classification:safe.error,latency_ms:Date.now()-started});
      return {isError:true,content:[{type:'text' as const,text:JSON.stringify({...safe,mcp_version:contract.runtime_release,deployment_release:deploymentReleaseId,agent_id:agentId})}]};
    }
  });
  return server;
}
