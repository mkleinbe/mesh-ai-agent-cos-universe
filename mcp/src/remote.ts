import fs from 'node:fs';
import http, { type IncomingMessage, type ServerResponse } from 'node:http';
import { createMcpHandler } from '@modelcontextprotocol/server';
import { toNodeHandler } from '@modelcontextprotocol/node';
import { callPythonBridge } from './python-bridge.js';
import { createServer, loadContract, requireAgentId, requireDeploymentRelease, type MCPContract } from './server.js';

const NATIVE_SLACK_MODE = 'CHATGPT_NATIVE_EVENT_TRIGGER';

function ip(req:IncomingMessage):string { return (req.socket.remoteAddress??'').replace(/^::ffff:/,''); }
function allowed(req:IncomingMessage,env:NodeJS.ProcessEnv):boolean { const expected=env.MCP_TRUSTED_CLIENT_IP?.trim(); return Boolean(expected)&&ip(req)===expected; }
function json(res:ServerResponse,status:number,value:unknown){ const out=JSON.stringify(value); res.writeHead(status,{'content-type':'application/json','content-length':Buffer.byteLength(out)}); res.end(out); }

function protectedFilePresent(pathValue:string|undefined):boolean {
  const target=pathValue?.trim();
  if(!target) return false;
  try { return fs.statSync(target).isFile(); } catch { return false; }
}

export function nativeSlackHitlConfigured(env:NodeJS.ProcessEnv=process.env):boolean {
  return (env.MESH_COS_SLACK_HITL_MODE??'').trim()===NATIVE_SLACK_MODE
    && (env.MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID??'').trim()==='C0BRL4GCL3A'
    && (env.MESH_COS_SLACK_APPROVER_PRINCIPAL??'').trim()==='michael'
    && (env.MESH_COS_SLACK_APP_ID??'').trim()==='A0B49RNE4K0'
    && protectedFilePresent(env.MESH_COS_SLACK_APPROVER_USER_ID_FILE)
    && protectedFilePresent(env.MESH_COS_SLACK_BOT_TOKEN_FILE)
    && !(env.MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE??'').trim();
}

function statusPayload(ok:boolean,contract:MCPContract,agentId:string,deploymentRelease:string,slackHitlReady:boolean){
  return {ok,mcp_version:contract.runtime_release,deployment_release:deploymentRelease,agent_id:agentId,transport:'SECURE_MCP_TUNNEL',slack_hitl_mode:NATIVE_SLACK_MODE,slack_hitl_ready:slackHitlReady};
}

async function runtimeCoreReady(env:NodeJS.ProcessEnv):Promise<void>{
  const contract=loadContract();
  const agent=requireAgentId(contract,env);
  const r=await callPythonBridge({tool_name:'registry.get_agent',arguments:{agent_id:agent}},env);
  const record=r.result as {status?:string};
  if(record?.status!=='ACTIVE') throw new Error('bound_agent_not_active');
  await callPythonBridge({tool_name:'governance.verify_audit_chain',arguments:{}},env);
}

async function runtimeReady(env:NodeJS.ProcessEnv):Promise<void>{
  await runtimeCoreReady(env);
  if(!nativeSlackHitlConfigured(env)) throw new Error('native_slack_hitl_not_configured');
}

function discoveryRequest(deploymentRelease:string):Request {
  return new Request('http://mesh-cos-mcp.internal/mcp',{
    method:'POST',
    headers:{
      'content-type':'application/json',
      'accept':'application/json, text/event-stream',
      'MCP-Protocol-Version':'2026-07-28',
      'Mcp-Method':'server/discover',
    },
    body:JSON.stringify({
      jsonrpc:'2.0',
      id:'readiness-discover',
      method:'server/discover',
      params:{
        _meta:{
          'io.modelcontextprotocol/protocolVersion':'2026-07-28',
          'io.modelcontextprotocol/clientCapabilities':{},
          'io.modelcontextprotocol/clientInfo':{name:'mesh-cos-readiness',version:deploymentRelease},
        },
      },
    }),
  });
}

async function protocolReady(handler:ReturnType<typeof createMcpHandler>,deploymentRelease:string):Promise<void>{
  const response=await handler.fetch(discoveryRequest(deploymentRelease));
  const text=await response.text();
  if(response.status!==200||!text.includes('2026-07-28')) throw new Error('modern_mcp_discovery_unavailable');
}

export async function startRemote(env:NodeJS.ProcessEnv=process.env){
  if((env.MCP_AUTH_MODE??'').trim()!=='tunnel') throw new Error('Remote MCP requires MCP_AUTH_MODE=tunnel; controlled HTTPS OAuth is not enabled by this deployment');
  if(!env.MCP_TRUSTED_CLIENT_IP?.trim()) throw new Error('MCP_TRUSTED_CLIENT_IP is required');

  const contract=loadContract();
  const agentId=requireAgentId(contract,env);
  const deploymentRelease=requireDeploymentRelease(env);
  const handler=createMcpHandler(()=>createServer(env,contract));
  const nodeHandler=toNodeHandler(handler);

  await runtimeCoreReady(env);
  await protocolReady(handler,deploymentRelease);

  const app=http.createServer(async(req,res)=>{
    try {
      const url=new URL(req.url??'/',`http://${req.headers.host??'localhost'}`);
      const slackReady=nativeSlackHitlConfigured(env);
      if(url.pathname==='/healthz') return json(res,200,statusPayload(true,contract,agentId,deploymentRelease,slackReady));
      if(url.pathname==='/readyz'){
        try{
          await runtimeReady(env);
          await protocolReady(handler,deploymentRelease);
          return json(res,200,statusPayload(true,contract,agentId,deploymentRelease,true));
        }catch{
          return json(res,503,statusPayload(false,contract,agentId,deploymentRelease,slackReady));
        }
      }
      if(url.pathname!=='/mcp') return json(res,404,{error:'not_found'});
      if(!allowed(req,env)) return json(res,403,{error:'forbidden'});
      await nodeHandler(req,res);
    } catch {
      if(!res.headersSent) json(res,500,{error:'mcp_transport_error'});
      else res.end();
    }
  });

  const port=Number(env.MCP_PORT??'8080');
  const host=env.MCP_BIND_HOST??'0.0.0.0';
  await new Promise<void>((resolve,reject)=>{ app.once('error',reject); app.listen(port,host,()=>resolve()); });
  const stop=async()=>{
    await new Promise<void>(resolve=>app.close(()=>resolve()));
    await handler.close();
  };
  process.once('SIGTERM',()=>void stop().finally(()=>process.exit(0)));
  process.once('SIGINT',()=>void stop().finally(()=>process.exit(0)));
  return app;
}

await startRemote();
