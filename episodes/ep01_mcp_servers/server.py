from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agents-institute-demo", log_level="WARNING")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


if __name__ == "__main__":
    mcp.run()  # stdio transport; mcp.run("sse") serves HTTP + SSE instead
