"""
Ticket data models for the ticketing system.
Follows Azure development best practices for data modeling.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class TicketStatus(str, Enum):
    """Ticket status enumeration."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, Enum):
    """Ticket priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketCategory(str, Enum):
    """Ticket category enumeration."""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    ACCESS = "access"
    PERFORMANCE = "performance"
    SECURITY = "security"
    OTHER = "other"

# SQLAlchemy ORM Model
class TicketORM(Base):
    """SQLAlchemy ORM model for tickets."""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN, index=True)
    priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM, index=True)
    category = Column(SQLEnum(TicketCategory), default=TicketCategory.OTHER, index=True)
    assignee = Column(String(100), nullable=True, index=True)
    reporter = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    tags = Column(Text, nullable=True)  # JSON string for tags
    resolution_notes = Column(Text, nullable=True)

# Pydantic Models for API
class TicketBase(BaseModel):
    """Base ticket model."""
    title: str = Field(..., min_length=1, max_length=255, description="Ticket title")
    description: str = Field(..., min_length=1, description="Detailed description of the issue")
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM, description="Ticket priority")
    category: TicketCategory = Field(default=TicketCategory.OTHER, description="Ticket category")
    assignee: Optional[str] = Field(None, max_length=100, description="Assigned user")
    reporter: str = Field(..., max_length=100, description="User who reported the issue")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()

class TicketCreate(TicketBase):
    """Model for creating tickets."""
    pass

class TicketUpdate(BaseModel):
    """Model for updating tickets."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    assignee: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    resolution_notes: Optional[str] = None

class Ticket(TicketBase):
    """Complete ticket model with all fields."""
    id: int
    status: TicketStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class TicketSearchRequest(BaseModel):
    """Model for ticket search requests."""
    query: str = Field(..., min_length=1, description="Search query")
    status: Optional[List[TicketStatus]] = Field(None, description="Filter by status")
    priority: Optional[List[TicketPriority]] = Field(None, description="Filter by priority")
    category: Optional[List[TicketCategory]] = Field(None, description="Filter by category")
    assignee: Optional[str] = Field(None, description="Filter by assignee")
    reporter: Optional[str] = Field(None, description="Filter by reporter")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    use_semantic_search: bool = Field(default=True, description="Use semantic search")

class TicketSearchResult(BaseModel):
    """Model for ticket search results."""
    tickets: List[Ticket]
    total_count: int
    search_time_ms: float
    query: str

class TicketAnalytics(BaseModel):
    """Model for ticket analytics."""
    total_tickets: int
    open_tickets: int
    closed_tickets: int
    avg_resolution_time_hours: Optional[float] = None
    tickets_by_status: Dict[str, int]
    tickets_by_priority: Dict[str, int]
    tickets_by_category: Dict[str, int]
    recent_activity: List[Dict[str, Any]]

# MCP-specific models for tool responses
class MCPTicketResponse(BaseModel):
    """Response model for MCP ticket operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MCPTicketListResponse(BaseModel):
    """Response model for MCP ticket list operations."""
    success: bool
    message: str
    tickets: List[Dict[str, Any]]
    total_count: int
    error: Optional[str] = None
