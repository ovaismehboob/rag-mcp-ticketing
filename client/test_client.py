"""
Test script for the Semantic Kernel MCP Client.
Run this to verify the client is working correctly.
"""
import asyncio
import sys
from pathlib import Path

# Add client to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_client():
    """Test the client components."""
    print("🚀 Testing Semantic Kernel MCP Client")
    print("=" * 50)
    
    try:
        # Test 1: Import configuration
        print("\n📝 Test 1: Configuration...")
        from config import settings
        print(f"   ✅ App name: {settings.app_name}")
        print(f"   ✅ Server URL: {settings.mcp_server_url}")
        print(f"   ✅ Azure OpenAI endpoint configured: {bool(settings.azure_openai_endpoint)}")
        
        # Test 2: MCP Client
        print("\n🔌 Test 2: MCP Client connection...")
        from mcp_client import mcp_client
        
        try:
            tools = await mcp_client.get_available_tools()
            if tools and "tools" in tools and len(tools["tools"]) > 0:
                print(f"   ✅ Connected to MCP server")
                print(f"   ✅ Available tools: {len(tools['tools'])}")
            else:
                print(f"   ⚠️  MCP server responded but no tools available")
        except Exception as e:
            print(f"   ❌ MCP connection failed: {e}")
            print(f"   💡 Make sure the MCP server is running on {settings.mcp_server_url}")
        
        # Test 3: Semantic Kernel Agent (basic import)
        print("\n🧠 Test 3: Semantic Kernel Agent...")
        from semantic_agent import semantic_agent, SEMANTIC_KERNEL_AVAILABLE
        
        if SEMANTIC_KERNEL_AVAILABLE:
            print("   ✅ Semantic Kernel available")
            try:
                await semantic_agent.initialize()
                print("   ✅ Semantic Kernel agent initialized")
            except Exception as e:
                print(f"   ❌ Semantic Kernel initialization failed: {e}")
                print("   💡 Check your Azure OpenAI configuration")
        else:
            print("   ⚠️  Semantic Kernel not installed")
            print("   💡 Run: pip install -r requirements.txt")
        
        # Test 4: Web Application Import
        print("\n🌐 Test 4: Web application...")
        from main import app
        print("   ✅ FastAPI application imported successfully")
        
        print("\n🎉 Client tests completed!")
        print("\n💡 Next steps:")
        print("   1. Copy .env.example to .env and configure your Azure OpenAI settings")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Start MCP server: uvicorn app.main:app --reload --port 8000")
        print("   4. Start client: python main.py")
        print("   5. Open http://localhost:8001 in your browser")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏁 Starting client tests...\n")
    
    success = asyncio.run(test_client())
    if not success:
        print("\n🔧 Some tests failed. Check the output above.")
        sys.exit(1)
    else:
        print(f"\n🎯 Client is ready for configuration!")
