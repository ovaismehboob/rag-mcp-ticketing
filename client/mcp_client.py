"""
MCP Client for connecting to the ticketing API and providing MCP tools to Semantic Kernel.
"""
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
import httpx
from config import settings

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for connecting to MCP server and accessing tools."""
    
    def __init__(self, server_url: str = None):
        """Initialize the MCP client."""
        self.server_url = server_url or settings.mcp_server_url
        self.timeout = settings.mcp_server_timeout
        self._tools_cache = None
        
    async def get_available_tools(self) -> Dict[str, Any]:
        """Get list of available MCP tools from the server."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.server_url}/mcp/tools")
                response.raise_for_status()
                
                tools_data = response.json()
                self._tools_cache = tools_data
                
                logger.info(f"Retrieved {len(tools_data.get('tools', []))} MCP tools")
                return tools_data
                
        except Exception as e:
            logger.error(f"Failed to get MCP tools: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool with arguments."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "tool_name": tool_name,
                    "parameters": arguments  # Changed from "arguments" to "parameters"
                }
                
                response = await client.post(
                    f"{self.server_url}/mcp/call_tool",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Successfully called tool '{tool_name}'")
                return result
                
        except Exception as e:
            logger.error(f"Failed to call tool '{tool_name}': {e}")
            raise
    
    async def search_tickets(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search tickets using semantic search."""
        return await self.call_tool("search_tickets", {
            "query": query,
            "limit": limit,
            "use_semantic_search": True
        })
    
    async def create_ticket(self, title: str, description: str, priority: str = "medium", 
                          category: str = "other", reporter: str = "user@example.com") -> Dict[str, Any]:
        """Create a new ticket."""
        return await self.call_tool("create_ticket", {
            "title": title,
            "description": description,
            "priority": priority,
            "category": category,
            "reporter": reporter
        })
    
    async def get_ticket(self, ticket_id: int) -> Dict[str, Any]:
        """Get a specific ticket by ID."""
        return await self.call_tool("get_ticket", {
            "ticket_id": ticket_id
        })
    
    async def list_tickets(self, limit: int = 10, status: str = None) -> Dict[str, Any]:
        """List tickets with optional filtering."""
        args = {"limit": limit}
        if status:
            args["status"] = [status]
        return await self.call_tool("list_tickets", args)
    
    async def update_ticket(self, ticket_id: int, **updates) -> Dict[str, Any]:
        """Update a ticket with new information."""
        return await self.call_tool("update_ticket", {
            "ticket_id": ticket_id,
            **updates
        })
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get ticket analytics and insights."""
        return await self.call_tool("get_ticket_analytics", {})
    
    async def suggest_resolution(self, ticket_id: int) -> Dict[str, Any]:
        """Get AI-powered resolution suggestions for a ticket."""
        return await self.call_tool("suggest_resolution", {
            "ticket_id": ticket_id
        })

# Global MCP client instance
mcp_client = MCPClient()
