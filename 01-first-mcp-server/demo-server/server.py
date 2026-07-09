from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two integer numbers
    Args:
        a: first integer
        b: second integer

    Return:
        sum of the two integers
    """
    return a + b


if __name__ == "__main__":
    mcp.run(transport='streamable-http')