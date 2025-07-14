"""
REST API router for ticket operations.
Provides traditional REST endpoints alongside MCP functionality.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from ..models.ticket import (
    Ticket, TicketCreate, TicketUpdate, TicketSearchRequest, 
    TicketSearchResult, TicketAnalytics, TicketStatus, 
    TicketPriority, TicketCategory
)
from ..services import ticket_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Dependency to ensure service is initialized
async def get_ticket_service():
    """Dependency to get initialized ticket service."""
    await ticket_service.initialize()
    return ticket_service

@router.post("/", response_model=Ticket, status_code=201)
async def create_ticket(
    ticket_data: TicketCreate,
    service = Depends(get_ticket_service)
):
    """Create a new incident ticket."""
    try:
        ticket = await service.create_ticket(ticket_data)
        return ticket
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Ticket])
async def list_tickets(
    skip: int = Query(0, ge=0, description="Number of tickets to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tickets to return"),
    status: Optional[List[TicketStatus]] = Query(None, description="Filter by status"),
    priority: Optional[List[TicketPriority]] = Query(None, description="Filter by priority"),
    category: Optional[List[TicketCategory]] = Query(None, description="Filter by category"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    reporter: Optional[str] = Query(None, description="Filter by reporter"),
    service = Depends(get_ticket_service)
):
    """List tickets with optional filtering and pagination."""
    try:
        tickets = await service.list_tickets(
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
            category=category,
            assignee=assignee,
            reporter=reporter
        )
        return tickets
    except Exception as e:
        logger.error(f"Error listing tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: int,
    service = Depends(get_ticket_service)
):
    """Get a specific ticket by ID."""
    try:
        ticket = await service.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    service = Depends(get_ticket_service)
):
    """Update an existing ticket."""
    try:
        ticket = await service.update_ticket(ticket_id, ticket_data)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(
    ticket_id: int,
    service = Depends(get_ticket_service)
):
    """Delete a ticket."""
    try:
        success = await service.delete_ticket(ticket_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=TicketSearchResult)
async def search_tickets(
    search_request: TicketSearchRequest,
    service = Depends(get_ticket_service)
):
    """Search tickets using semantic search and RAG."""
    try:
        results = await service.search_tickets(search_request)
        
        search_result = TicketSearchResult(
            tickets=results["tickets"],
            total_count=results["total_count"],
            search_time_ms=results["search_time_ms"],
            query=results["query"]
        )
        
        return search_result
    except Exception as e:
        logger.error(f"Error searching tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/summary", response_model=TicketAnalytics)
async def get_ticket_analytics(
    service = Depends(get_ticket_service)
):
    """Get ticket analytics and statistics."""
    try:
        analytics = await service.get_ticket_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Error getting ticket analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}/insights")
async def get_ticket_insights(
    ticket_id: int,
    service = Depends(get_ticket_service)
):
    """Get AI-generated insights for a specific ticket."""
    try:
        insights = await service.get_ticket_with_ai_insights(ticket_id)
        if not insights:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return insights
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}/similar")
async def get_similar_tickets(
    ticket_id: int,
    limit: int = Query(5, ge=1, le=20, description="Number of similar tickets to return"),
    service = Depends(get_ticket_service)
):
    """Get tickets similar to the specified ticket."""
    try:
        ticket = await service.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        
        from ..services.vector_store import vector_store
        similar_results = await vector_store.get_similar_tickets(ticket, limit + 1)
        
        # Remove the original ticket from results and get ticket details
        similar_ticket_ids = [tid for tid, score in similar_results if tid != ticket_id][:limit]
        
        similar_tickets = []
        for tid in similar_ticket_ids:
            similar_ticket = await service.get_ticket(tid)
            if similar_ticket:
                similar_tickets.append(similar_ticket)
        
        return {
            "ticket_id": ticket_id,
            "similar_tickets": similar_tickets,
            "total_found": len(similar_tickets)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting similar tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))
