#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the client directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'client'))

from mcp_client import mcp_client

async def test_mcp_client():
    """Test MCP client functionality."""
    try:
        print("Testing MCP client...")
        
        # Test list_tickets
        print("\n1. Testing list_tickets...")
        result = await mcp_client.list_tickets()
        print(f"Result: {result}")
        
        # Test create_ticket
        print("\n2. Testing create_ticket...")
        result = await mcp_client.create_ticket(
            title="Test ticket from client test",
            description="This is a test ticket to verify MCP client functionality",
            priority="medium",
            reporter="test@example.com"
        )
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_client())
