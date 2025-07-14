import asyncio
import httpx

async def test_mcp():
    async with httpx.AsyncClient() as client:
        resp = await client.get('http://127.0.0.1:8000/mcp/tools')
        print("MCP Tools Response:")
        print(resp.json())

if __name__ == "__main__":
    asyncio.run(test_mcp())
