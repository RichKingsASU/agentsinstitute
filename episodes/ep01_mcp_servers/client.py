"""Spawn server.py over stdio, do the MCP handshake, list tools, call one."""
import asyncio
import sys
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    t0 = time.perf_counter()
    async with stdio_client(params) as (r, w), ClientSession(r, w) as s:
        init = await s.initialize()
        print(f"<- initialize  server={init.serverInfo.name} protocol={init.protocolVersion}")
        tools = await s.list_tools()
        print(f"<- tools/list  {[t.name for t in tools.tools]}")
        res = await s.call_tool("add", {"a": 40, "b": 2})
        print(f"<- tools/call  add(40, 2) = {res.content[0].text}")
    elapsed = time.perf_counter() - t0
    assert [t.name for t in tools.tools] == ["add"] and res.content[0].text == "42"
    assert elapsed < 5, f"spawn + handshake + call took {elapsed:.2f}s"
    print(f"PASS  3 round trips over stdio in {elapsed * 1000:.0f} ms (< 5 s)")


asyncio.run(main())
