"""
Ticket service for business logic and database operations.
Follows Azure best practices for data access and business logic separation.
"""
import logging
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from ..config import settings
from ..models.ticket import (
    TicketORM, Ticket, TicketCreate, TicketUpdate, TicketStatus, 
    TicketPriority, TicketCategory, TicketSearchRequest, TicketAnalytics,
    Base
)
from .vector_store import vector_store
from .rag_service import rag_service

logger = logging.getLogger(__name__)

class TicketService:
    """Service for ticket operations with integrated RAG capabilities."""
    
    def __init__(self):
        """Initialize the ticket service."""
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connection with proper error handling."""
        if self._initialized:
            return
        
        try:
            # Create database engine
            self.engine = create_engine(
                settings.database_url,
                echo=settings.debug,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600    # Recycle connections every hour
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Initialize vector store
            await vector_store.initialize()
            
            # Initialize RAG service
            await rag_service.initialize()
            
            self._initialized = True
            logger.info("Ticket service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ticket service: {e}")
            raise
    
    def get_db(self) -> Session:
        """Get database session with proper error handling."""
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        
        db = self.SessionLocal()
        try:
            return db
        except Exception as e:
            db.close()
            raise
    
    async def create_ticket(self, ticket_data: TicketCreate) -> Ticket:
        """Create a new ticket with vector store integration."""
        try:
            await self.initialize()
            
            db = self.get_db()
            try:
                # Create ORM object
                db_ticket = TicketORM(
                    title=ticket_data.title,
                    description=ticket_data.description,
                    priority=ticket_data.priority,
                    category=ticket_data.category,
                    assignee=ticket_data.assignee,
                    reporter=ticket_data.reporter,
                    tags=json.dumps(ticket_data.tags or [])
                )
                
                # Add to database
                db.add(db_ticket)
                db.commit()
                db.refresh(db_ticket)
                
                # Convert to Pydantic model
                ticket = self._orm_to_pydantic(db_ticket)
                
                # Add to vector store asynchronously
                await vector_store.add_ticket(ticket)
                
                logger.info(f"Created ticket {ticket.id}")
                return ticket
                
            finally:
                db.close()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error creating ticket: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create ticket: {e}")
            raise
    
    async def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """Get a ticket by ID."""
        try:
            await self.initialize()
            
            db = self.get_db()
            try:
                db_ticket = db.query(TicketORM).filter(TicketORM.id == ticket_id).first()
                if not db_ticket:
                    return None
                
                return self._orm_to_pydantic(db_ticket)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to get ticket {ticket_id}: {e}")
            raise
    
    async def list_tickets(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[List[TicketStatus]] = None,
        priority: Optional[List[TicketPriority]] = None,
        category: Optional[List[TicketCategory]] = None,
        assignee: Optional[str] = None,
        reporter: Optional[str] = None
    ) -> List[Ticket]:
        """List tickets with filtering options."""
        try:
            await self.initialize()
            
            db = self.get_db()
            try:
                query = db.query(TicketORM)
                
                # Apply filters
                if status:
                    query = query.filter(TicketORM.status.in_(status))
                if priority:
                    query = query.filter(TicketORM.priority.in_(priority))
                if category:
                    query = query.filter(TicketORM.category.in_(category))
                if assignee:
                    query = query.filter(TicketORM.assignee == assignee)
                if reporter:
                    query = query.filter(TicketORM.reporter == reporter)
                
                # Apply pagination and ordering
                db_tickets = query.order_by(TicketORM.created_at.desc()).offset(skip).limit(limit).all()
                
                return [self._orm_to_pydantic(ticket) for ticket in db_tickets]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to list tickets: {e}")
            raise
    
    async def update_ticket(self, ticket_id: int, ticket_data: TicketUpdate) -> Optional[Ticket]:
        """Update a ticket with vector store synchronization."""
        try:
            await self.initialize()
            
            db = self.get_db()
            try:
                db_ticket = db.query(TicketORM).filter(TicketORM.id == ticket_id).first()
                if not db_ticket:
                    return None
                
                # Update fields
                update_data = ticket_data.dict(exclude_unset=True)
                for field, value in update_data.items():
                    if field == "tags" and value is not None:
                        value = json.dumps(value)
                    setattr(db_ticket, field, value)
                
                # Set resolved timestamp if status changed to resolved/closed
                if ticket_data.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
                    if not db_ticket.resolved_at:
                        db_ticket.resolved_at = datetime.utcnow()
                
                db.commit()
                db.refresh(db_ticket)
                
                # Convert to Pydantic model
                ticket = self._orm_to_pydantic(db_ticket)
                
                # Update vector store
                await vector_store.update_ticket(ticket)
                
                logger.info(f"Updated ticket {ticket_id}")
                return ticket
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to update ticket {ticket_id}: {e}")
            raise
    
    async def delete_ticket(self, ticket_id: int) -> bool:
        """Delete a ticket and remove from vector store."""
        try:
            await self.initialize()
            
            db = self.get_db()
            try:
                db_ticket = db.query(TicketORM).filter(TicketORM.id == ticket_id).first()
                if not db_ticket:
                    return False
                
                db.delete(db_ticket)
                db.commit()
                
                # Remove from vector store
                await vector_store.remove_ticket(ticket_id)
                
                logger.info(f"Deleted ticket {ticket_id}")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to delete ticket {ticket_id}: {e}")
            raise
    
    async def search_tickets(self, search_request: TicketSearchRequest) -> Dict[str, Any]:
        """Search tickets using RAG-enhanced search."""
        try:
            await self.initialize()
            
            start_time = datetime.now()
            
            # Use RAG service for enhanced search
            search_results = await rag_service.search_tickets_with_context(search_request)
            ticket_ids = search_results.get("ticket_ids", [])
            
            # Fetch full ticket data
            tickets = []
            if ticket_ids:
                db = self.get_db()
                try:
                    db_tickets = db.query(TicketORM).filter(TicketORM.id.in_(ticket_ids)).all()
                    
                    # Maintain order from search results
                    ticket_map = {ticket.id: self._orm_to_pydantic(ticket) for ticket in db_tickets}
                    tickets = [ticket_map[tid] for tid in ticket_ids if tid in ticket_map]
                    
                finally:
                    db.close()
            
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "tickets": tickets,
                "total_count": len(tickets),
                "search_time_ms": search_time,
                "query": search_request.query,
                "similarity_scores": search_results.get("similarity_scores", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to search tickets: {e}")
            raise
    
    async def get_ticket_analytics(self) -> TicketAnalytics:
        """Get ticket analytics and statistics."""
        try:
            await self.initialize()
            
            db = self.get_db()
            try:
                # Basic counts
                total_tickets = db.query(TicketORM).count()
                open_tickets = db.query(TicketORM).filter(
                    TicketORM.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.PENDING])
                ).count()
                closed_tickets = db.query(TicketORM).filter(
                    TicketORM.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED])
                ).count()
                
                # Tickets by status
                status_counts = {}
                for status in TicketStatus:
                    count = db.query(TicketORM).filter(TicketORM.status == status).count()
                    status_counts[status.value] = count
                
                # Tickets by priority
                priority_counts = {}
                for priority in TicketPriority:
                    count = db.query(TicketORM).filter(TicketORM.priority == priority).count()
                    priority_counts[priority.value] = count
                
                # Tickets by category
                category_counts = {}
                for category in TicketCategory:
                    count = db.query(TicketORM).filter(TicketORM.category == category).count()
                    category_counts[category.value] = count
                
                # Calculate average resolution time
                resolved_tickets = db.query(TicketORM).filter(
                    and_(
                        TicketORM.resolved_at.isnot(None),
                        TicketORM.created_at.isnot(None)
                    )
                ).all()
                
                avg_resolution_time = None
                if resolved_tickets:
                    total_hours = sum([
                        (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                        for ticket in resolved_tickets
                    ])
                    avg_resolution_time = total_hours / len(resolved_tickets)
                
                # Recent activity (last 10 updates)
                recent_tickets = db.query(TicketORM).order_by(
                    TicketORM.updated_at.desc()
                ).limit(10).all()
                
                recent_activity = []
                for ticket in recent_tickets:
                    activity = {
                        "ticket_id": ticket.id,
                        "title": ticket.title,
                        "status": ticket.status.value,
                        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else ticket.created_at.isoformat()
                    }
                    recent_activity.append(activity)
                
                return TicketAnalytics(
                    total_tickets=total_tickets,
                    open_tickets=open_tickets,
                    closed_tickets=closed_tickets,
                    avg_resolution_time_hours=avg_resolution_time,
                    tickets_by_status=status_counts,
                    tickets_by_priority=priority_counts,
                    tickets_by_category=category_counts,
                    recent_activity=recent_activity
                )
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to get ticket analytics: {e}")
            raise
    
    async def get_ticket_with_ai_insights(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Get ticket with AI-generated insights."""
        try:
            ticket = await self.get_ticket(ticket_id)
            if not ticket:
                return None
            
            # Generate AI insights
            summary = await rag_service.generate_ticket_summary(ticket)
            resolution_suggestion = await rag_service.suggest_resolution(ticket)
            sentiment_analysis = await rag_service.analyze_ticket_sentiment(ticket)
            
            # Find similar tickets
            similar_tickets_data = await vector_store.get_similar_tickets(ticket, limit=5)
            similar_ticket_ids = [tid for tid, score in similar_tickets_data if tid != ticket.id]
            
            return {
                "ticket": ticket.dict(),
                "ai_insights": {
                    "summary": summary,
                    "resolution_suggestion": resolution_suggestion,
                    "sentiment_analysis": sentiment_analysis,
                    "similar_ticket_ids": similar_ticket_ids[:3]  # Top 3 similar
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get ticket with AI insights: {e}")
            raise
    
    def _orm_to_pydantic(self, db_ticket: TicketORM) -> Ticket:
        """Convert SQLAlchemy ORM model to Pydantic model."""
        tags = []
        if db_ticket.tags:
            try:
                tags = json.loads(db_ticket.tags)
            except json.JSONDecodeError:
                tags = []
        
        return Ticket(
            id=db_ticket.id,
            title=db_ticket.title,
            description=db_ticket.description,
            status=db_ticket.status,
            priority=db_ticket.priority,
            category=db_ticket.category,
            assignee=db_ticket.assignee,
            reporter=db_ticket.reporter,
            created_at=db_ticket.created_at,
            updated_at=db_ticket.updated_at,
            resolved_at=db_ticket.resolved_at,
            tags=tags,
            resolution_notes=db_ticket.resolution_notes
        )

# Global instance
ticket_service = TicketService()
