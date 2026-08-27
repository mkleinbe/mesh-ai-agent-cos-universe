import http, { type IncomingMessage, type ServerResponse } from 'node:http';
import { createMcpHandler } from '@modelcontextprotocol/server';
import { toNodeHandler } from '@modelcontextprotocol/node';
import { callPythonBridge } from './python-bridge.js';
import { createServer, loadContract, requireAgentId, requireDeploymentRelease, type MCPContract } from './server.js';
import { SlackSocketModeApprovalListener } from './slack-socket-mode.js';

function ip(req:IncomingMessage):string { return (req.socket.remoteAddress??'').replace(/^::ffff:/,''); }
function allowed(req:IncomingMessage,env:NodeJS.ProcessEnv):boolean { const expected=env.MCP_TRUSTED_CLIENT_IP?.trim(); return Boolean(expected)&&ip(req)===expected; }
function json(res:ServerResponse,status:number,value:unknown){ const out=JSON.stringify(value); res.writeHead(status,{'content-type':'application/json','content-length':Buffer.byteLength(out)}); res.end(out); }
function statusPayload(ok:boolean,contract:MCPContract,agentId:string,deploymentRelease:string,slackHitlReady:boolean){
  return {ok,mcp_version:contract.runtime_release,deployment_release:deploymentRelease,agent_id:agentId,transport:'SECURE_MCP_TUNNEL',slack_hitl_ready:slackHitlReady};
}

async function runtimeCoreReady(env:NodeJS.ProcessEnv):Promise<void>{
  const contract=loadContract();
  const agent=requireAgentId(contract,env);
  const r=await callPythonBridge({tool_name:'registry.get_agent',arguments:{agent_id:agent}},env);
  const record=r.result as {status?:string};
  if(record?.status!=='ACTIVE') throw new Error('bound_agent_not_active');
  await callPythonBridge({tool_name:'governance.verify_audit_chain',arguments:{}},env);
}

async function runtimeReady(env:NodeJS.ProcessEnv,slack:SlackSocketModeApprovalListener):Promise<void>{
  await runtimeCoreReady(env);
  if(!slack.isActive()) throw new Error('slack_hitl_unavailable');
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
  const slackHitl=new SlackSocketModeApprovalListener(env);

  // Validate local Slack configuration and start the provider connection loop, but do not
  // make Slack availability a process-startup dependency. Consequential readiness remains
  // fail-closed through /readyz while /healthz proves the MCP process itself is alive.
  await slackHitl.start();
  await runtimeCoreReady(env);
  await protocolReady(handler,deploymentRelease);

  const app=http.createServer(async(req,res)=>{
    try {
      const url=new URL(req.url??'/',`http://${req.headers.host??'localhost'}`);
      if(url.pathname==='/healthz') return json(res,200,statusPayload(true,contract,agentId,deploymentRelease,slackHitl.isActive()));
      if(url.pathname==='/readyz'){
        try{
          await runtimeReady(env,slackHitl);
          await protocolReady(handler,deploymentRelease);
          return json(res,200,statusPayload(true,contract,agentId,deploymentRelease,true));
        }catch{
          return json(res,503,statusPayload(false,contract,agentId,deploymentRelease,slackHitl.isActive()));
        }
      }
      if(url.pathname!=='/mcp') return json(res,404,{error:'not_found'});
      // The Secure MCP Tunnel private source identity remains the remote ingress trust boundary.
      // Do not weaken or bypass this check when changing protocol handling.
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
    await slackHitl.stop();
    await new Promise<void>(resolve=>app.close(()=>resolve()));
    await handler.close();
  };
  process.once('SIGTERM',()=>void stop().finally(()=>process.exit(0)));
  process.once('SIGINT',()=>void stop().finally(()=>process.exit(0)));
  return app;
}

await startRemote();
