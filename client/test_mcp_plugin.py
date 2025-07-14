"""
Test script for the MCPSsePlugin implementation.
"""
import asyncio
import logging
from semantic_agent_mcp import semantic_mcp_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_plugin():
    """Test the MCPSsePlugin integration."""
    print("🧪 Testing MCPSsePlugin Integration")
    print("=" * 50)
    
    try:
        # Initialize the agent
        print("\n1. Initializing Semantic Kernel with MCPSsePlugin...")
        await semantic_mcp_agent.initialize()
        print("   ✅ Agent initialized successfully")
        
        # Test getting available tools
        print("\n2. Getting available MCP tools...")
        tools = await semantic_mcp_agent.get_available_tools()
        print(f"   ✅ Found {len(tools)} MCP tools:")
        for tool in tools:
            print(f"      - {tool['name']}: {tool['description']}")
        
        # Test chat functionality
        print("\n3. Testing chat with MCP tools...")
        test_queries = [
            "Create a test ticket for testing MCPSsePlugin integration",
            "List all available tickets",
            "Search for tickets about testing"
        ]
        
        for query in test_queries:
            print(f"\n   Query: {query}")
            response = await semantic_mcp_agent.chat(query)
            print(f"   Response: {response[:200]}...")
        
        print("\n🎉 MCPSsePlugin test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n4. Cleaning up...")
        await semantic_mcp_agent.cleanup()
        print("   ✅ Cleanup completed")

if __name__ == "__main__":
    asyncio.run(test_mcp_plugin())
