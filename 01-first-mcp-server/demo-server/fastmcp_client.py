from fastmcp import Client
import asyncio


async def main():
    async with Client('http://localhost:8000/mcp') as client:
        if client.is_connected():
            print("MCP server connected")

        tools = await client.list_tools()
        for t in tools:
            print(f"{t.name}: {t.description}")

        tool_args = {'add': {'a': 3, 'b': 7}}
        res = await client.call_tool('add', tool_args['add'])
        print(f"{tool_args} -> {res}")

if __name__ == "__main__":
    asyncio.run(main())

