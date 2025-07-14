"""
Simple vector store service for basic RAG functionality.
This is a simplified version that provides basic text search without external dependencies.
"""
import logging
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from ..config import settings
from ..models.ticket import Ticket

logger = logging.getLogger(__name__)

class SimpleVectorStoreService:
    """Simple vector store service for basic text matching."""
    
    def __init__(self):
        """Initialize the simple vector store service."""
        self.tickets_store: Dict[int, Dict[str, Any]] = {}
        self._initialized = False
        
    async def initialize(self):
        """Initialize the vector store."""
        if self._initialized:
            return
        
        try:
            self.tickets_store = {}
            self._initialized = True
            logger.info("Simple vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def add_ticket(self, ticket: Ticket) -> bool:
        """Add a ticket to the vector store."""
        try:
            await self.initialize()
            
            # Create document text for searching
            document_text = self._create_document_text(ticket).lower()
            
            # Store ticket data with searchable text
            self.tickets_store[ticket.id] = {
                "ticket_id": ticket.id,
                "document_text": document_text,
                "title": ticket.title.lower(),
                "description": ticket.description.lower(),
                "status": ticket.status.value,
                "priority": ticket.priority.value,
                "category": ticket.category.value,
                "assignee": ticket.assignee or "",
                "reporter": ticket.reporter,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else "",
                "tags": " ".join(ticket.tags or []).lower()
            }
            
            logger.info(f"Added ticket {ticket.id} to simple vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add ticket {ticket.id} to vector store: {e}")
            return False
    
    async def update_ticket(self, ticket: Ticket) -> bool:
        """Update a ticket in the vector store."""
        try:
            await self.initialize()
            
            # Simply re-add the ticket (overwrite existing)
            return await self.add_ticket(ticket)
            
        except Exception as e:
            logger.error(f"Failed to update ticket {ticket.id} in vector store: {e}")
            return False
    
    async def remove_ticket(self, ticket_id: int) -> bool:
        """Remove a ticket from the vector store."""
        try:
            await self.initialize()
            
            if ticket_id in self.tickets_store:
                del self.tickets_store[ticket_id]
                logger.info(f"Removed ticket {ticket_id} from vector store")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove ticket {ticket_id} from vector store: {e}")
            return False
    
    async def search_tickets(
        self, 
        query: str, 
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[int, float]]:
        """
        Search for tickets using simple text matching.
        
        Returns:
            List of tuples (ticket_id, similarity_score)
        """
        try:
            await self.initialize()
            
            query_lower = query.lower()
            query_terms = query_lower.split()
            
            results = []
            
            for ticket_id, ticket_data in self.tickets_store.items():
                # Apply filters if provided
                if filters:
                    skip_ticket = False
                    for key, value in filters.items():
                        if value is not None:
                            if isinstance(value, list):
                                if ticket_data.get(key) not in value:
                                    skip_ticket = True
                                    break
                            else:
                                if ticket_data.get(key) != value:
                                    skip_ticket = True
                                    break
                    
                    if skip_ticket:
                        continue
                
                # Calculate simple text similarity
                document_text = ticket_data["document_text"]
                title = ticket_data["title"]
                description = ticket_data["description"]
                tags = ticket_data["tags"]
                
                # Count matching terms
                score = 0.0
                total_terms = len(query_terms)
                
                if total_terms > 0:
                    for term in query_terms:
                        # Title matches get higher weight
                        if term in title:
                            score += 3.0
                        # Description matches get medium weight
                        elif term in description:
                            score += 2.0
                        # Tag matches get medium weight
                        elif term in tags:
                            score += 2.0
                        # General document matches get lower weight
                        elif term in document_text:
                            score += 1.0
                    
                    # Normalize score (0-1 range)
                    score = score / (total_terms * 3.0)  # Max possible score is 3.0 per term
                
                # Also check for exact phrase matches (higher score)
                if query_lower in title:
                    score += 0.5
                elif query_lower in description:
                    score += 0.3
                
                if score > 0:
                    results.append((ticket_id, min(score, 1.0)))  # Cap at 1.0
            
            # Sort by score descending and limit results
            results.sort(key=lambda x: x[1], reverse=True)
            results = results[:limit]
            
            logger.info(f"Found {len(results)} tickets for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search tickets: {e}")
            return []
    
    async def get_similar_tickets(
        self, 
        ticket: Ticket, 
        limit: int = 5
    ) -> List[Tuple[int, float]]:
        """Find similar tickets to the given ticket."""
        try:
            # Use title and description as search query
            search_query = f"{ticket.title} {ticket.description}"
            results = await self.search_tickets(search_query, limit + 1)  # +1 to exclude self
            
            # Filter out the original ticket
            filtered_results = [(tid, score) for tid, score in results if tid != ticket.id]
            return filtered_results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find similar tickets for {ticket.id}: {e}")
            return []
    
    def _create_document_text(self, ticket: Ticket) -> str:
        """Create a text representation of the ticket for searching."""
        text_parts = [
            f"Title: {ticket.title}",
            f"Description: {ticket.description}",
            f"Status: {ticket.status.value}",
            f"Priority: {ticket.priority.value}",
            f"Category: {ticket.category.value}",
            f"Reporter: {ticket.reporter}"
        ]
        
        if ticket.assignee:
            text_parts.append(f"Assignee: {ticket.assignee}")
        
        if ticket.tags:
            text_parts.append(f"Tags: {', '.join(ticket.tags)}")
        
        if ticket.resolution_notes:
            text_parts.append(f"Resolution: {ticket.resolution_notes}")
        
        return " | ".join(text_parts)
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection."""
        try:
            await self.initialize()
            
            return {
                "total_documents": len(self.tickets_store),
                "collection_name": "simple_tickets_store",
                "embedding_model": "simple_text_matching"
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
    
    async def reset_collection(self) -> bool:
        """Reset the entire collection (use with caution)."""
        try:
            self.tickets_store = {}
            logger.warning("Vector collection has been reset")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False

# Global instance
vector_store = SimpleVectorStoreService()
