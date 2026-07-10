from fastmcp import Client
import asyncio


async def main():
    async with Client('http://localhost:8000/mcp') as client:
        if client.is_connected():
            print("MCP server connected")

        tools = await client.list_tools()
        for t in tools:
            print(f"{t.name}: {t.description}")

        tool_args = {'get_current_weather': {'location': "New York"}}
        res = await client.call_tool('get_current_weather', tool_args['get_current_weather'])
        print(f"{tool_args} -> {res}")

        tool_args = {'get_forecast_weather': {'location': "New York"}}
        res = await client.call_tool('get_forecast_weather', tool_args['get_forecast_weather'])
        print(f"{tool_args} -> {res}")

if __name__ == "__main__":
    asyncio.run(main())

