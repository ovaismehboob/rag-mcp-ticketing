"""
MCP (Model Context Protocol) Server implementation.
Exposes ticket management tools following MCP pattern for Semantic Kernel integration.
"""
import logging
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from pydantic import BaseModel, Field

from .models.mcp_models import (
    MCPTool, MCPToolParameter, MCPToolParameterType, MCPServerInfo,
    MCPListToolsResponse, MCPToolCall, MCPToolResponse
)
from .models.ticket import (
    TicketCreate, TicketUpdate, TicketSearchRequest, TicketStatus,
    TicketPriority, TicketCategory, MCPTicketResponse, MCPTicketListResponse
)
from .services import ticket_service, rag_service

logger = logging.getLogger(__name__)

class SimpleMCPServer:
    """Simple MCP Server for ticket management tools without external dependencies."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.tools: Dict[str, Callable] = {}
        self._register_tools()
    
    def tool(self, name: str = None):
        """Decorator to register MCP tools."""
        def decorator(func: Callable):
            tool_name = name or func.__name__
            self.tools[tool_name] = func
            return func
        return decorator
    
    def _register_tools(self):
        """Register all MCP tools."""
        
        @self.tool("create_ticket")
        async def create_ticket(
            title: str,
            description: str,
            priority: str = "medium",
            category: str = "other",
            assignee: Optional[str] = None,
            reporter: str = "",
            tags: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Create a new incident ticket."""
            try:
                # Validate enums
                try:
                    priority_enum = TicketPriority(priority.lower())
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Invalid priority: {priority}. Must be one of: {[p.value for p in TicketPriority]}"
                    }
                
                try:
                    category_enum = TicketCategory(category.lower())
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Invalid category: {category}. Must be one of: {[c.value for c in TicketCategory]}"
                    }
                
                # Create ticket
                ticket_data = TicketCreate(
                    title=title,
                    description=description,
                    priority=priority_enum,
                    category=category_enum,
                    assignee=assignee,
                    reporter=reporter,
                    tags=tags
                )
                
                ticket = await ticket_service.create_ticket(ticket_data)
                
                return {
                    "success": True,
                    "message": f"Ticket created successfully with ID {ticket.id}",
                    "data": {
                        "ticket_id": ticket.id,
                        "title": ticket.title,
                        "status": ticket.status.value,
                        "created_at": ticket.created_at.isoformat()
                    }
                }
                
            except Exception as e:
                logger.error(f"Error creating ticket: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.tool("list_tickets")
        async def list_tickets(
            status: Optional[List[str]] = None,
            priority: Optional[List[str]] = None,
            category: Optional[List[str]] = None,
            assignee: Optional[str] = None,
            reporter: Optional[str] = None,
            limit: int = 10
        ) -> Dict[str, Any]:
            """List tickets with optional filtering."""
            try:
                # Convert string enums to enum objects
                status_enums = None
                if status:
                    try:
                        status_enums = [TicketStatus(s.lower()) for s in status]
                    except ValueError as e:
                        return {
                            "success": False,
                            "error": f"Invalid status value: {e}"
                        }
                
                priority_enums = None
                if priority:
                    try:
                        priority_enums = [TicketPriority(p.lower()) for p in priority]
                    except ValueError as e:
                        return {
                            "success": False,
                            "error": f"Invalid priority value: {e}"
                        }
                
                category_enums = None
                if category:
                    try:
                        category_enums = [TicketCategory(c.lower()) for c in category]
                    except ValueError as e:
                        return {
                            "success": False,
                            "error": f"Invalid category value: {e}"
                        }
                
                # Fetch tickets
                tickets = await ticket_service.list_tickets(
                    limit=limit,
                    status=status_enums,
                    priority=priority_enums,
                    category=category_enums,
                    assignee=assignee,
                    reporter=reporter
                )
                
                # Convert to serializable format
                ticket_data = []
                for ticket in tickets:
                    ticket_dict = {
                        "id": ticket.id,
                        "title": ticket.title,
                        "description": ticket.description[:200] + "..." if len(ticket.description) > 200 else ticket.description,
                        "status": ticket.status.value,
                        "priority": ticket.priority.value,
                        "category": ticket.category.value,
                        "assignee": ticket.assignee,
                        "reporter": ticket.reporter,
                        "created_at": ticket.created_at.isoformat(),
                        "tags": ticket.tags
                    }
                    ticket_data.append(ticket_dict)
                
                return {
                    "success": True,
                    "message": f"Found {len(tickets)} tickets",
                    "tickets": ticket_data,
                    "total_count": len(tickets)
                }
                
            except Exception as e:
                logger.error(f"Error listing tickets: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "tickets": [],
                    "total_count": 0
                }
        
        @self.tool("get_ticket")
        async def get_ticket(
            ticket_id: int,
            include_ai_insights: bool = False
        ) -> Dict[str, Any]:
            """Get detailed information about a specific ticket."""
            try:
                if include_ai_insights:
                    ticket_data = await ticket_service.get_ticket_with_ai_insights(ticket_id)
                    if not ticket_data:
                        return {
                            "success": False,
                            "error": f"Ticket {ticket_id} not found"
                        }
                    
                    return {
                        "success": True,
                        "message": f"Retrieved ticket {ticket_id} with AI insights",
                        "data": ticket_data
                    }
                else:
                    ticket = await ticket_service.get_ticket(ticket_id)
                    if not ticket:
                        return {
                            "success": False,
                            "error": f"Ticket {ticket_id} not found"
                        }
                    
                    return {
                        "success": True,
                        "message": f"Retrieved ticket {ticket_id}",
                        "data": {
                            "id": ticket.id,
                            "title": ticket.title,
                            "description": ticket.description,
                            "status": ticket.status.value,
                            "priority": ticket.priority.value,
                            "category": ticket.category.value,
                            "assignee": ticket.assignee,
                            "reporter": ticket.reporter,
                            "created_at": ticket.created_at.isoformat(),
                            "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
                            "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
                            "tags": ticket.tags,
                            "resolution_notes": ticket.resolution_notes
                        }
                    }
                
            except Exception as e:
                logger.error(f"Error getting ticket {ticket_id}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.tool("update_ticket")
        async def update_ticket(
            ticket_id: int,
            title: Optional[str] = None,
            description: Optional[str] = None,
            status: Optional[str] = None,
            priority: Optional[str] = None,
            category: Optional[str] = None,
            assignee: Optional[str] = None,
            resolution_notes: Optional[str] = None,
            tags: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Update an existing ticket."""
            try:
                # Build update data
                update_data = {}
                
                if title is not None:
                    update_data["title"] = title
                if description is not None:
                    update_data["description"] = description
                if status is not None:
                    try:
                        update_data["status"] = TicketStatus(status.lower())
                    except ValueError:
                        return {
                            "success": False,
                            "error": f"Invalid status: {status}"
                        }
                if priority is not None:
                    try:
                        update_data["priority"] = TicketPriority(priority.lower())
                    except ValueError:
                        return {
                            "success": False,
                            "error": f"Invalid priority: {priority}"
                        }
                if category is not None:
                    try:
                        update_data["category"] = TicketCategory(category.lower())
                    except ValueError:
                        return {
                            "success": False,
                            "error": f"Invalid category: {category}"
                        }
                if assignee is not None:
                    update_data["assignee"] = assignee
                if resolution_notes is not None:
                    update_data["resolution_notes"] = resolution_notes
                if tags is not None:
                    update_data["tags"] = tags
                
                if not update_data:
                    return {
                        "success": False,
                        "error": "No fields to update provided"
                    }
                
                # Update ticket
                ticket_update = TicketUpdate(**update_data)
                ticket = await ticket_service.update_ticket(ticket_id, ticket_update)
                
                if not ticket:
                    return {
                        "success": False,
                        "error": f"Ticket {ticket_id} not found"
                    }
                
                return {
                    "success": True,
                    "message": f"Ticket {ticket_id} updated successfully",
                    "data": {
                        "id": ticket.id,
                        "title": ticket.title,
                        "status": ticket.status.value,
                        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None
                    }
                }
                
            except Exception as e:
                logger.error(f"Error updating ticket {ticket_id}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.tool("search_tickets")
        async def search_tickets(
            query: str,
            limit: int = 10,
            use_semantic_search: bool = True
        ) -> Dict[str, Any]:
            """Search tickets using semantic search and RAG."""
            try:
                search_request = TicketSearchRequest(
                    query=query,
                    limit=limit,
                    use_semantic_search=use_semantic_search
                )
                
                results = await ticket_service.search_tickets(search_request)
                
                # Convert tickets to serializable format
                ticket_data = []
                for ticket in results["tickets"]:
                    ticket_dict = {
                        "id": ticket.id,
                        "title": ticket.title,
                        "description": ticket.description[:200] + "..." if len(ticket.description) > 200 else ticket.description,
                        "status": ticket.status.value,
                        "priority": ticket.priority.value,
                        "category": ticket.category.value,
                        "similarity_score": results["similarity_scores"].get(ticket.id, 0.0)
                    }
                    ticket_data.append(ticket_dict)
                
                return {
                    "success": True,
                    "message": f"Found {len(ticket_data)} tickets matching '{query}'",
                    "tickets": ticket_data,
                    "total_count": results["total_count"],
                    "search_time_ms": results["search_time_ms"]
                }
                
            except Exception as e:
                logger.error(f"Error searching tickets: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "tickets": [],
                    "total_count": 0
                }
        
        @self.tool("get_ticket_analytics")
        async def get_ticket_analytics() -> Dict[str, Any]:
            """Get ticket statistics and analytics."""
            try:
                analytics = await ticket_service.get_ticket_analytics()
                
                return {
                    "success": True,
                    "message": "Analytics retrieved successfully",
                    "data": {
                        "total_tickets": analytics.total_tickets,
                        "open_tickets": analytics.open_tickets,
                        "closed_tickets": analytics.closed_tickets,
                        "avg_resolution_time_hours": analytics.avg_resolution_time_hours,
                        "tickets_by_status": analytics.tickets_by_status,
                        "tickets_by_priority": analytics.tickets_by_priority,
                        "tickets_by_category": analytics.tickets_by_category,
                        "recent_activity": analytics.recent_activity
                    }
                }
                
            except Exception as e:
                logger.error(f"Error getting ticket analytics: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.tool("generate_ticket_insights")
        async def generate_ticket_insights(
            ticket_ids: Optional[List[int]] = None,
            limit: int = 50
        ) -> Dict[str, Any]:
            """Generate AI-powered insights from ticket data."""
            try:
                if ticket_ids:
                    # Get specific tickets
                    tickets = []
                    for ticket_id in ticket_ids:
                        ticket = await ticket_service.get_ticket(ticket_id)
                        if ticket:
                            tickets.append(ticket)
                else:
                    # Get recent tickets
                    tickets = await ticket_service.list_tickets(limit=limit)
                
                if not tickets:
                    return {
                        "success": False,
                        "error": "No tickets found for analysis"
                    }
                
                # Generate insights using RAG service
                insights = await rag_service.generate_ticket_insights(tickets)
                
                if not insights:
                    return {
                        "success": False,
                        "error": "Unable to generate insights (AI service may be unavailable)"
                    }
                
                return {
                    "success": True,
                    "message": f"Generated insights for {len(tickets)} tickets",
                    "data": insights
                }
                
            except Exception as e:
                logger.error(f"Error generating ticket insights: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a registered tool."""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }
        
        try:
            tool_func = self.tools[tool_name]
            result = await tool_func(**parameters)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global MCP server instance
mcp_server = SimpleMCPServer()
