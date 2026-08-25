import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { createServer, loadContract, requireLocalStdioContract } from './server.js';

const contract=loadContract();
requireLocalStdioContract(contract);
void serveStdio(()=>createServer(process.env,contract));
