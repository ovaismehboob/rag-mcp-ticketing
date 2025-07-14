"""
MCP API router for Model Context Protocol endpoints.
Exposes MCP tools and prompts for Semantic Kernel integration.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..models.mcp_models import (
    MCPListToolsResponse, MCPToolCall, MCPToolResponse,
    MCPServerInfo, MCPTool, MCPToolParameter, MCPToolParameterType
)
from ..mcp_server import mcp_server
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])

@router.get("/info", response_model=MCPServerInfo)
async def get_server_info():
    """Get MCP server information and capabilities."""
    try:
        tools = [
            MCPTool(
                name="create_ticket",
                description="Create a new incident ticket",
                parameters={
                    "title": MCPToolParameter(type=MCPToolParameterType.STRING, description="Ticket title", required=True),
                    "description": MCPToolParameter(type=MCPToolParameterType.STRING, description="Detailed description", required=True),
                    "priority": MCPToolParameter(type=MCPToolParameterType.STRING, description="Priority level", required=False, enum=["low", "medium", "high", "critical"]),
                    "category": MCPToolParameter(type=MCPToolParameterType.STRING, description="Issue category", required=False, enum=["hardware", "software", "network", "access", "performance", "security", "other"]),
                    "assignee": MCPToolParameter(type=MCPToolParameterType.STRING, description="Assigned user", required=False),
                    "reporter": MCPToolParameter(type=MCPToolParameterType.STRING, description="Reporting user", required=True),
                    "tags": MCPToolParameter(type=MCPToolParameterType.ARRAY, description="Tags list", required=False)
                }
            ),
            MCPTool(
                name="list_tickets",
                description="List tickets with optional filtering",
                parameters={
                    "status": MCPToolParameter(type=MCPToolParameterType.ARRAY, description="Filter by status", required=False),
                    "priority": MCPToolParameter(type=MCPToolParameterType.ARRAY, description="Filter by priority", required=False),
                    "category": MCPToolParameter(type=MCPToolParameterType.ARRAY, description="Filter by category", required=False),
                    "assignee": MCPToolParameter(type=MCPToolParameterType.STRING, description="Filter by assignee", required=False),
                    "reporter": MCPToolParameter(type=MCPToolParameterType.STRING, description="Filter by reporter", required=False),
                    "limit": MCPToolParameter(type=MCPToolParameterType.INTEGER, description="Maximum results", required=False)
                }
            ),
            MCPTool(
                name="get_ticket",
                description="Get detailed ticket information",
                parameters={
                    "ticket_id": MCPToolParameter(type=MCPToolParameterType.INTEGER, description="Ticket ID", required=True),
                    "include_ai_insights": MCPToolParameter(type=MCPToolParameterType.BOOLEAN, description="Include AI insights", required=False)
                }
            ),
            MCPTool(
                name="update_ticket",
                description="Update an existing ticket",
                parameters={
                    "ticket_id": MCPToolParameter(type=MCPToolParameterType.INTEGER, description="Ticket ID", required=True),
                    "title": MCPToolParameter(type=MCPToolParameterType.STRING, description="New title", required=False),
                    "description": MCPToolParameter(type=MCPToolParameterType.STRING, description="New description", required=False),
                    "status": MCPToolParameter(type=MCPToolParameterType.STRING, description="New status", required=False),
                    "priority": MCPToolParameter(type=MCPToolParameterType.STRING, description="New priority", required=False),
                    "category": MCPToolParameter(type=MCPToolParameterType.STRING, description="New category", required=False),
                    "assignee": MCPToolParameter(type=MCPToolParameterType.STRING, description="New assignee", required=False),
                    "resolution_notes": MCPToolParameter(type=MCPToolParameterType.STRING, description="Resolution notes", required=False),
                    "tags": MCPToolParameter(type=MCPToolParameterType.ARRAY, description="New tags", required=False)
                }
            ),
            MCPTool(
                name="search_tickets",
                description="Search tickets using semantic search and RAG",
                parameters={
                    "query": MCPToolParameter(type=MCPToolParameterType.STRING, description="Search query", required=True),
                    "limit": MCPToolParameter(type=MCPToolParameterType.INTEGER, description="Maximum results", required=False),
                    "use_semantic_search": MCPToolParameter(type=MCPToolParameterType.BOOLEAN, description="Use AI search", required=False)
                }
            ),
            MCPTool(
                name="get_ticket_analytics",
                description="Get ticket statistics and analytics",
                parameters={}
            ),
            MCPTool(
                name="generate_ticket_insights",
                description="Generate AI-powered insights from ticket data",
                parameters={
                    "ticket_ids": MCPToolParameter(type=MCPToolParameterType.ARRAY, description="Specific ticket IDs", required=False),
                    "limit": MCPToolParameter(type=MCPToolParameterType.INTEGER, description="Number of tickets to analyze", required=False)
                }
            )
        ]
        
        server_info = MCPServerInfo(
            name=settings.mcp_server_name,
            version=settings.mcp_server_version,
            description="RAG-based ticketing system with MCP support for Semantic Kernel integration",
            capabilities=[
                "tools",
                "prompts", 
                "resources",
                "semantic_search",
                "ai_insights"
            ],
            tools=tools,
            prompts=[]  # We could add prompts later
        )
        
        return server_info
        
    except Exception as e:
        logger.error(f"Error getting server info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools", response_model=MCPListToolsResponse)
async def list_tools():
    """List all available MCP tools."""
    try:
        server_info = await get_server_info()
        return MCPListToolsResponse(tools=server_info.tools)
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/call_tool", response_model=MCPToolResponse)
async def call_tool(tool_call: MCPToolCall):
    """Execute an MCP tool call."""
    try:
        import time
        start_time = time.time()
        
        # Get the MCP server and call the tool
        result = await mcp_server.call_tool(tool_call.tool_name, tool_call.parameters)
        execution_time = (time.time() - start_time) * 1000
        
        return MCPToolResponse(
            success=result.get("success", False),
            result=result,
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error calling tool: {e}")
        return MCPToolResponse(
            success=False,
            error=str(e)
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for MCP server."""
    try:
        # Check if services are initialized
        from ..services import ticket_service, vector_store, rag_service
        
        await ticket_service.initialize()
        await vector_store.initialize()
        await rag_service.initialize()
        
        # Get basic stats
        stats = await vector_store.get_collection_stats()
        
        return {
            "status": "healthy",
            "server_name": settings.mcp_server_name,
            "version": settings.mcp_server_version,
            "services": {
                "ticket_service": "ready",
                "vector_store": "ready",
                "rag_service": "ready"
            },
            "vector_store_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@router.get("/prompts")
async def list_prompts():
    """List available MCP prompts (placeholder for future expansion)."""
    return {
        "prompts": [
            {
                "name": "ticket_analysis",
                "description": "Analyze ticket patterns and suggest improvements",
                "arguments": {
                    "time_period": {
                        "type": "string",
                        "description": "Analysis time period (e.g., '7d', '30d', '90d')",
                        "required": False
                    }
                }
            },
            {
                "name": "resolution_guide",
                "description": "Generate resolution guidance for specific ticket types",
                "arguments": {
                    "category": {
                        "type": "string", 
                        "description": "Ticket category to generate guidance for",
                        "required": True
                    }
                }
            }
        ]
    }
