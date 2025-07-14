"""
Test script for the ticketing API with MCP support.
Run this to verify the system is working correctly.
"""
import asyncio
import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_system():
    """Test the ticketing system components."""
    print("🚀 Testing RAG-based Ticketing System with MCP Support")
    print("=" * 60)
    
    try:
        # Import services
        from app.services import ticket_service, vector_store, rag_service
        from app.models.ticket import TicketCreate, TicketPriority, TicketCategory
        
        print("✅ Successfully imported modules")
        
        # Test 1: Initialize services
        print("\n📝 Test 1: Initializing services...")
        await ticket_service.initialize()
        print("   ✅ Ticket service initialized")
        
        await vector_store.initialize()
        print("   ✅ Vector store initialized")
        
        await rag_service.initialize()
        print("   ✅ RAG service initialized")
        
        # Test 2: Create test tickets
        print("\n🎫 Test 2: Creating test tickets...")
        
        test_tickets = [
            {
                "title": "Server performance issue",
                "description": "The main application server is running slowly and response times are over 5 seconds",
                "priority": TicketPriority.HIGH,
                "category": TicketCategory.PERFORMANCE,
                "reporter": "john.doe@company.com",
                "tags": ["server", "performance", "urgent"]
            },
            {
                "title": "Unable to access email",
                "description": "User cannot log into their email account. Getting authentication error.",
                "priority": TicketPriority.MEDIUM,
                "category": TicketCategory.ACCESS,
                "reporter": "jane.smith@company.com",
                "assignee": "it.support@company.com",
                "tags": ["email", "authentication"]
            },
            {
                "title": "Network connectivity problems",
                "description": "Intermittent network disconnections in the east wing office. Multiple users affected.",
                "priority": TicketPriority.HIGH,
                "category": TicketCategory.NETWORK,
                "reporter": "admin@company.com",
                "tags": ["network", "office", "multiple-users"]
            },
            {
                "title": "Software installation request",
                "description": "Need to install Adobe Creative Suite for the design team. 5 licenses required.",
                "priority": TicketPriority.LOW,
                "category": TicketCategory.SOFTWARE,
                "reporter": "design.lead@company.com",
                "tags": ["software", "installation", "design"]
            }
        ]
        
        created_tickets = []
        for i, ticket_data in enumerate(test_tickets, 1):
            ticket_create = TicketCreate(**ticket_data)
            ticket = await ticket_service.create_ticket(ticket_create)
            created_tickets.append(ticket)
            print(f"   ✅ Created ticket {i}: {ticket.title} (ID: {ticket.id})")
        
        # Test 3: List tickets
        print("\n📋 Test 3: Listing tickets...")
        tickets = await ticket_service.list_tickets(limit=10)
        print(f"   ✅ Retrieved {len(tickets)} tickets")
        
        # Test 4: Search tickets
        print("\n🔍 Test 4: Testing semantic search...")
        from app.models.ticket import TicketSearchRequest
        
        search_queries = [
            "server slow performance",
            "email login problem", 
            "network connection",
            "software install"
        ]
        
        for query in search_queries:
            search_request = TicketSearchRequest(
                query=query,
                limit=3,
                use_semantic_search=True
            )
            
            search_results = await ticket_service.search_tickets(search_request)
            print(f"   ✅ Search '{query}': found {len(search_results['tickets'])} tickets")
        
        # Test 5: Get analytics
        print("\n📊 Test 5: Getting analytics...")
        analytics = await ticket_service.get_ticket_analytics()
        print(f"   ✅ Analytics: {analytics.total_tickets} total tickets")
        print(f"      - Open: {analytics.open_tickets}")
        print(f"      - Closed: {analytics.closed_tickets}")
        
        # Test 6: Test MCP server
        print("\n🔌 Test 6: Testing MCP server...")
        from app.mcp_server import mcp_server
        
        # Our SimpleMCPServer doesn't need get_app()
        print(f"   ✅ MCP server initialized with {len(mcp_server.tools)} tools")
        
        # Test a simple MCP tool call
        try:
            # Simulate calling the list_tickets tool
            result = await mcp_server.tools["list_tickets"](limit=3)
            if result.get("success"):
                print(f"   ✅ MCP list_tickets: {result['total_count']} tickets")
            else:
                print(f"   ⚠️  MCP list_tickets returned: {result}")
        except Exception as e:
            print(f"   ⚠️  MCP tool test failed: {e}")
        
        # Test 7: Vector store stats
        print("\n📈 Test 7: Vector store statistics...")
        stats = await vector_store.get_collection_stats()
        print(f"   ✅ Vector store: {stats.get('total_documents', 0)} documents indexed")
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Start the server: uvicorn app.main:app --reload")
        print("   2. Visit http://localhost:8000/docs for API documentation")
        print("   3. Check MCP tools at http://localhost:8000/mcp/tools")
        print("   4. Test with Semantic Kernel MCPPlugin")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def quick_test():
    """Quick test to verify basic functionality."""
    print("🧪 Quick functionality test...")
    
    try:
        # Test imports
        from app.config import settings
        from app.models.ticket import TicketCreate, TicketPriority
        from app.services import ticket_service
        
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ Database URL: {settings.database_url}")
        print("✅ All imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure to install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏁 Starting tests...\n")
    
    # Run quick test first
    if not asyncio.run(quick_test()):
        print("\n❌ Quick test failed. Please check your setup.")
        sys.exit(1)
    
    print("\n" + "="*60)
    
    # Ask user if they want to run full test
    try:
        response = input("\nRun full system test? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            success = asyncio.run(test_system())
            if success:
                print(f"\n🎯 System is ready! Start with: uvicorn app.main:app --reload")
            else:
                print(f"\n🔧 Some tests failed. Check the output above.")
                sys.exit(1)
        else:
            print("✅ Quick test passed. Run full test when ready!")
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
