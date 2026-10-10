"""Spawn server.py over stdio, do the MCP handshake, list tools, call one."""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with stdio_client(params) as (r, w), ClientSession(r, w) as s:
        init = await s.initialize()
        print(f"<- initialize  server={init.serverInfo.name} protocol={init.protocolVersion}")
        tools = await s.list_tools()
        print(f"<- tools/list  {[t.name for t in tools.tools]}")
        res = await s.call_tool("add", {"a": 40, "b": 2})
        print(f"<- tools/call  add(40, 2) = {res.content[0].text}")


asyncio.run(main())
