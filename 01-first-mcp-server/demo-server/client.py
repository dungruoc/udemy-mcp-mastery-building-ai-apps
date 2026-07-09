import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    server_url = 'http://127.0.0.1:8000/mcp/'
    async with streamablehttp_client(server_url) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            print("Not initialized, session_id:", get_session_id())
            await session.initialize()
            sid = get_session_id()
            print("Initialized, session_id:", sid)

            result = await session.call_tool("add", {'a': 2, 'b': 3})
            print("Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
