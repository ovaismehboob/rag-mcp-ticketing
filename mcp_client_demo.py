"""
Example MCP client for testing Semantic Kernel integration.
This demonstrates how to interact with the MCP server.
"""
import asyncio
import json
import httpx
from typing import Dict, Any, List

class MCPClient:
    """Simple MCP client for testing the ticketing API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the MCP client."""
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information."""
        response = await self.client.get(f"{self.base_url}/mcp/info")
        response.raise_for_status()
        return response.json()
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools."""
        response = await self.client.get(f"{self.base_url}/mcp/tools")
        response.raise_for_status()
        return response.json()["tools"]
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        payload = {
            "tool_name": tool_name,
            "parameters": parameters
        }
        response = await self.client.post(f"{self.base_url}/mcp/call_tool", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check MCP server health."""
        response = await self.client.get(f"{self.base_url}/mcp/health")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()

async def demo_mcp_integration():
    """Demonstrate MCP integration with the ticketing system."""
    print("🔌 MCP Client Demo - Ticketing System Integration")
    print("=" * 60)
    
    client = MCPClient()
    
    try:
        # 1. Check server health
        print("\n🏥 Checking server health...")
        health = await client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Services: {list(health.get('services', {}).keys())}")
        
        # 2. Get server info
        print("\n📋 Getting server information...")
        server_info = await client.get_server_info()
        print(f"   Server: {server_info['name']} v{server_info['version']}")
        print(f"   Capabilities: {', '.join(server_info['capabilities'])}")
        print(f"   Available tools: {len(server_info['tools'])}")
        
        # 3. List tools
        print("\n🛠️  Available MCP Tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # 4. Demo: Create a ticket
        print("\n🎫 Demo 1: Creating a ticket via MCP...")
        create_result = await client.call_tool("create_ticket", {
            "title": "MCP Test Ticket",
            "description": "This ticket was created through the MCP interface to test integration",
            "priority": "medium",
            "category": "other",
            "reporter": "mcp.client@test.com",
            "tags": ["mcp", "test", "integration"]
        })
        
        if create_result["success"]:
            ticket_id = create_result["result"]["data"]["ticket_id"]
            print(f"   ✅ Created ticket ID: {ticket_id}")
        else:
            print(f"   ❌ Failed to create ticket: {create_result.get('error')}")
            return
        
        # 5. Demo: List tickets
        print("\n📋 Demo 2: Listing tickets via MCP...")
        list_result = await client.call_tool("list_tickets", {
            "limit": 5
        })
        
        if list_result["success"]:
            tickets = list_result["result"]["tickets"]
            print(f"   ✅ Found {len(tickets)} tickets")
            for ticket in tickets[:3]:  # Show first 3
                print(f"      - ID {ticket['id']}: {ticket['title']} ({ticket['status']})")
        else:
            print(f"   ❌ Failed to list tickets: {list_result.get('error')}")
        
        # 6. Demo: Get ticket details
        print("\n🔍 Demo 3: Getting ticket details with AI insights...")
        get_result = await client.call_tool("get_ticket", {
            "ticket_id": ticket_id,
            "include_ai_insights": True
        })
        
        if get_result["success"]:
            ticket_data = get_result["result"]["data"]
            print(f"   ✅ Retrieved ticket: {ticket_data.get('ticket', {}).get('title', 'Unknown')}")
            
            ai_insights = ticket_data.get("ai_insights", {})
            if ai_insights.get("summary"):
                print(f"   🤖 AI Summary: {ai_insights['summary'][:100]}...")
        else:
            print(f"   ❌ Failed to get ticket: {get_result.get('error')}")
        
        # 7. Demo: Search tickets
        print("\n🔍 Demo 4: Semantic search via MCP...")
        search_result = await client.call_tool("search_tickets", {
            "query": "test integration",
            "limit": 3,
            "use_semantic_search": True
        })
        
        if search_result["success"]:
            tickets = search_result["result"]["tickets"]
            print(f"   ✅ Search found {len(tickets)} tickets")
            for ticket in tickets:
                score = ticket.get("similarity_score", 0)
                print(f"      - {ticket['title']} (similarity: {score:.3f})")
        else:
            print(f"   ❌ Search failed: {search_result.get('error')}")
        
        # 8. Demo: Get analytics
        print("\n📊 Demo 5: Getting analytics via MCP...")
        analytics_result = await client.call_tool("get_ticket_analytics", {})
        
        if analytics_result["success"]:
            data = analytics_result["result"]["data"]
            print(f"   ✅ Analytics:")
            print(f"      - Total tickets: {data['total_tickets']}")
            print(f"      - Open tickets: {data['open_tickets']}")
            print(f"      - By priority: {data['tickets_by_priority']}")
        else:
            print(f"   ❌ Analytics failed: {analytics_result.get('error')}")
        
        # 9. Demo: Update ticket
        print("\n✏️  Demo 6: Updating ticket via MCP...")
        update_result = await client.call_tool("update_ticket", {
            "ticket_id": ticket_id,
            "status": "in_progress",
            "assignee": "mcp.support@test.com",
            "resolution_notes": "Working on this ticket via MCP interface"
        })
        
        if update_result["success"]:
            print(f"   ✅ Updated ticket {ticket_id}")
        else:
            print(f"   ❌ Update failed: {update_result.get('error')}")
        
        print("\n🎉 MCP Demo completed successfully!")
        print("\n🔗 Integration with Semantic Kernel:")
        print("""
        # Example Semantic Kernel integration:
        from semantic_kernel import Kernel
        from semantic_kernel.connectors.mcp import MCPPlugin
        
        kernel = Kernel()
        mcp_plugin = MCPPlugin(server_url="http://localhost:8000/mcp")
        kernel.add_plugin(mcp_plugin, plugin_name="ticketing")
        
        # Now you can use the ticketing tools in your AI prompts:
        response = await kernel.invoke("ticketing", "create_ticket", {
            "title": "AI generated ticket",
            "description": "This ticket was created by an AI agent"
        })
        """)
        
    except httpx.RequestError as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

# Example Semantic Kernel integration code
SEMANTIC_KERNEL_EXAMPLE = '''
"""
Example: Using the MCP Ticketing System with Semantic Kernel
"""
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.mcp import MCPPlugin

async def semantic_kernel_demo():
    """Demonstrate using the ticketing MCP server with Semantic Kernel."""
    
    # Initialize Semantic Kernel
    kernel = Kernel()
    
    # Add OpenAI service
    kernel.add_service(OpenAIChatCompletion(
        ai_model_id="gpt-3.5-turbo",
        api_key="your-api-key"
    ))
    
    # Add MCP Plugin for ticketing
    mcp_plugin = MCPPlugin(
        server_url="http://localhost:8000/mcp",
        plugin_name="ticketing"
    )
    kernel.add_plugin(mcp_plugin, plugin_name="ticketing")
    
    # Create a prompt template that uses ticketing tools
    prompt = """
    You are an IT support assistant. Help users with their tickets.
    
    User request: {{$user_input}}
    
    Available tools:
    - create_ticket: Create new support tickets
    - list_tickets: List existing tickets  
    - search_tickets: Search for tickets
    - get_ticket_analytics: Get ticket statistics
    
    Use the appropriate tools to help the user.
    """
    
    # Execute with user input
    user_input = "Create a ticket for printer not working in office 302"
    
    response = await kernel.invoke(
        prompt,
        user_input=user_input
    )
    
    print(f"AI Response: {response}")

# Run this after setting up Semantic Kernel
# asyncio.run(semantic_kernel_demo())
'''

if __name__ == "__main__":
    print("🏁 Starting MCP client demo...\n")
    
    try:
        asyncio.run(demo_mcp_integration())
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print(f"\n📝 Semantic Kernel Example Code:")
    print("-" * 40)
    print(SEMANTIC_KERNEL_EXAMPLE)
