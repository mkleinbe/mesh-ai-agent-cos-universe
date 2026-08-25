import http, { type IncomingMessage, type ServerResponse } from 'node:http';
import { createMcpHandler } from '@modelcontextprotocol/server';
import { toNodeHandler } from '@modelcontextprotocol/node';
import { callPythonBridge } from './python-bridge.js';
import { createServer, loadContract, requireAgentId } from './server.js';

function ip(req:IncomingMessage):string { return (req.socket.remoteAddress??'').replace(/^::ffff:/,''); }
function allowed(req:IncomingMessage,env:NodeJS.ProcessEnv):boolean { const expected=env.MCP_TRUSTED_CLIENT_IP?.trim(); return Boolean(expected)&&ip(req)===expected; }
function json(res:ServerResponse,status:number,value:unknown){ const out=JSON.stringify(value); res.writeHead(status,{'content-type':'application/json','content-length':Buffer.byteLength(out)}); res.end(out); }

async function runtimeReady(env:NodeJS.ProcessEnv):Promise<void>{
  const contract=loadContract();
  const agent=requireAgentId(contract,env);
  const r=await callPythonBridge({tool_name:'registry.get_agent',arguments:{agent_id:agent}},env);
  const record=r.result as {status?:string};
  if(record?.status!=='ACTIVE') throw new Error('bound_agent_not_active');
  await callPythonBridge({tool_name:'governance.verify_audit_chain',arguments:{}},env);
}

function discoveryRequest():Request {
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
          'io.modelcontextprotocol/clientInfo':{name:'mesh-cos-readiness',version:'4.1.4'},
        },
      },
    }),
  });
}

async function protocolReady(handler:ReturnType<typeof createMcpHandler>):Promise<void>{
  const response=await handler.fetch(discoveryRequest());
  const text=await response.text();
  if(response.status!==200||!text.includes('2026-07-28')) throw new Error('modern_mcp_discovery_unavailable');
}

export async function startRemote(env:NodeJS.ProcessEnv=process.env){
  if((env.MCP_AUTH_MODE??'').trim()!=='tunnel') throw new Error('Remote MCP requires MCP_AUTH_MODE=tunnel; controlled HTTPS OAuth is not enabled by this deployment');
  if(!env.MCP_TRUSTED_CLIENT_IP?.trim()) throw new Error('MCP_TRUSTED_CLIENT_IP is required');

  const handler=createMcpHandler(()=>createServer(env));
  const nodeHandler=toNodeHandler(handler);
  await runtimeReady(env);
  await protocolReady(handler);

  const app=http.createServer(async(req,res)=>{
    try {
      const url=new URL(req.url??'/',`http://${req.headers.host??'localhost'}`);
      if(url.pathname==='/healthz') return json(res,200,{ok:true});
      if(url.pathname==='/readyz'){
        try{
          await runtimeReady(env);
          await protocolReady(handler);
          return json(res,200,{ok:true});
        }catch{
          return json(res,503,{ok:false});
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
    await new Promise<void>(resolve=>app.close(()=>resolve()));
    await handler.close();
  };
  process.once('SIGTERM',()=>void stop().finally(()=>process.exit(0)));
  process.once('SIGINT',()=>void stop().finally(()=>process.exit(0)));
  return app;
}

await startRemote();
