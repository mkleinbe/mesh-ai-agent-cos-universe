import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { createServer, loadContract, requireLocalStdioContract } from './server.js';
const contract=loadContract(); requireLocalStdioContract(contract); const server=createServer(process.env,contract); const transport=new StdioServerTransport(); await server.connect(transport);
