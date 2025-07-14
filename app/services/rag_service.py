"""
Simple RAG (Retrieval-Augmented Generation) service for ticket responses.
This is a basic implementation without external AI dependencies.
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..config import settings
from ..models.ticket import Ticket, TicketSearchRequest
from .vector_store import vector_store

logger = logging.getLogger(__name__)

class SimpleRAGService:
    """Simple RAG service for basic ticket analysis without external AI dependencies."""
    
    def __init__(self):
        """Initialize the simple RAG service."""
        self._initialized = False
    
    async def initialize(self):
        """Initialize the RAG service."""
        if self._initialized:
            return
        
        try:
            self._initialized = True
            logger.info("Simple RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    async def search_tickets_with_context(
        self, 
        search_request: TicketSearchRequest
    ) -> Dict[str, Any]:
        """
        Search tickets and provide contextual information.
        """
        try:
            await self.initialize()
            
            start_time = datetime.now()
            
            # Perform vector search if enabled
            if search_request.use_semantic_search:
                # Build filters for vector search
                filters = {}
                if search_request.status:
                    filters['status'] = [s.value for s in search_request.status]
                if search_request.priority:
                    filters['priority'] = [p.value for p in search_request.priority]
                if search_request.category:
                    filters['category'] = [c.value for c in search_request.category]
                if search_request.assignee:
                    filters['assignee'] = search_request.assignee
                if search_request.reporter:
                    filters['reporter'] = search_request.reporter
                
                # Search using vector store
                ticket_results = await vector_store.search_tickets(
                    query=search_request.query,
                    limit=search_request.limit,
                    filters=filters
                )
                
                # Extract ticket IDs and scores
                ticket_ids = [result[0] for result in ticket_results]
                similarity_scores = {result[0]: result[1] for result in ticket_results}
                
            else:
                # Fallback to simple text matching (implement as needed)
                ticket_ids = []
                similarity_scores = {}
            
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "ticket_ids": ticket_ids,
                "similarity_scores": similarity_scores,
                "search_time_ms": search_time,
                "total_results": len(ticket_ids)
            }
            
        except Exception as e:
            logger.error(f"Failed to search tickets with context: {e}")
            raise
    
    async def generate_ticket_summary(self, ticket: Ticket) -> Optional[str]:
        """Generate a basic summary of a ticket (no AI required)."""
        try:
            await self.initialize()
            
            # Create a simple rule-based summary
            priority_text = {
                "low": "low priority",
                "medium": "medium priority", 
                "high": "high priority",
                "critical": "critical priority"
            }
            
            category_text = {
                "hardware": "hardware-related",
                "software": "software-related",
                "network": "network-related",
                "access": "access-related",
                "performance": "performance-related",
                "security": "security-related",
                "other": "general"
            }
            
            # Build summary
            summary_parts = [
                f"This is a {priority_text.get(ticket.priority.value, 'unknown')} {category_text.get(ticket.category.value, 'general')} issue",
                f"reported by {ticket.reporter}"
            ]
            
            if ticket.assignee:
                summary_parts.append(f"assigned to {ticket.assignee}")
            
            summary_parts.append(f"with status: {ticket.status.value.replace('_', ' ')}")
            
            # Add description preview
            desc_preview = ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description
            summary_parts.append(f"Description: {desc_preview}")
            
            return ". ".join(summary_parts) + "."
            
        except Exception as e:
            logger.error(f"Failed to generate ticket summary: {e}")
            return None
    
    async def suggest_resolution(self, ticket: Ticket) -> Optional[str]:
        """Suggest resolution steps based on ticket category and priority."""
        try:
            await self.initialize()
            
            # Rule-based resolution suggestions
            category_suggestions = {
                "hardware": [
                    "1. Check physical connections and power supply",
                    "2. Run hardware diagnostics",
                    "3. Check for firmware updates", 
                    "4. Contact hardware vendor if under warranty"
                ],
                "software": [
                    "1. Restart the application or service",
                    "2. Check for software updates",
                    "3. Review error logs for specific issues",
                    "4. Reinstall software if necessary"
                ],
                "network": [
                    "1. Check network cable connections",
                    "2. Restart network equipment (router, switch)",
                    "3. Test connectivity with ping/traceroute",
                    "4. Contact network administrator"
                ],
                "access": [
                    "1. Verify user credentials",
                    "2. Check account status and permissions",
                    "3. Reset password if necessary",
                    "4. Contact system administrator"
                ],
                "performance": [
                    "1. Monitor system resource usage",
                    "2. Close unnecessary applications",
                    "3. Clear temporary files and cache",
                    "4. Consider system upgrade if resources are insufficient"
                ],
                "security": [
                    "1. Run security scan immediately",
                    "2. Change all passwords",
                    "3. Review access logs",
                    "4. Contact security team"
                ]
            }
            
            suggestions = category_suggestions.get(ticket.category.value, [
                "1. Gather more information about the issue",
                "2. Document steps to reproduce the problem",
                "3. Check system logs for errors",
                "4. Escalate to appropriate technical team"
            ])
            
            # Add priority-specific notes
            priority_notes = {
                "critical": "⚠️ URGENT: This is a critical issue requiring immediate attention.",
                "high": "⏰ HIGH PRIORITY: Address this issue as soon as possible.",
                "medium": "📋 MEDIUM PRIORITY: Address within normal business hours.",
                "low": "📝 LOW PRIORITY: Can be addressed during routine maintenance."
            }
            
            resolution_text = priority_notes.get(ticket.priority.value, "")
            if resolution_text:
                resolution_text += "\n\n"
            
            resolution_text += "Suggested resolution steps:\n" + "\n".join(suggestions)
            
            # Add estimated timeline
            timeline_estimates = {
                "critical": "Target resolution: Within 1 hour",
                "high": "Target resolution: Within 4 hours", 
                "medium": "Target resolution: Within 24 hours",
                "low": "Target resolution: Within 1 week"
            }
            
            timeline = timeline_estimates.get(ticket.priority.value, "Target resolution: As resources permit")
            resolution_text += f"\n\n{timeline}"
            
            return resolution_text
            
        except Exception as e:
            logger.error(f"Failed to suggest resolution: {e}")
            return None
    
    async def analyze_ticket_sentiment(self, ticket: Ticket) -> Optional[Dict[str, Any]]:
        """Analyze the sentiment and urgency of a ticket using simple rules."""
        try:
            await self.initialize()
            
            # Simple keyword-based sentiment analysis
            urgent_keywords = ["urgent", "critical", "emergency", "asap", "immediately", "broken", "down", "failed"]
            negative_keywords = ["frustrated", "angry", "unacceptable", "terrible", "awful", "worst"]
            positive_keywords = ["thank", "appreciate", "good", "excellent", "working"]
            
            text_to_analyze = f"{ticket.title} {ticket.description}".lower()
            
            # Count keyword occurrences
            urgent_count = sum(1 for word in urgent_keywords if word in text_to_analyze)
            negative_count = sum(1 for word in negative_keywords if word in text_to_analyze)
            positive_count = sum(1 for word in positive_keywords if word in text_to_analyze)
            
            # Determine sentiment
            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > 0 or urgent_count > 0:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Determine urgency
            if ticket.priority.value == "critical" or urgent_count >= 2:
                urgency = "critical"
            elif ticket.priority.value == "high" or urgent_count >= 1:
                urgency = "high"
            elif ticket.priority.value == "medium":
                urgency = "medium"
            else:
                urgency = "low"
            
            # Generate key concerns
            concerns = []
            if urgent_count > 0:
                concerns.append("User indicates urgency")
            if negative_count > 0:
                concerns.append("User expresses frustration")
            if ticket.priority.value in ["critical", "high"]:
                concerns.append("High priority issue")
            if not concerns:
                concerns.append("Standard support request")
            
            # Recommended action
            if urgency == "critical":
                action = "immediate"
            elif urgency == "high":
                action = "priority"
            else:
                action = "standard"
            
            analysis = f"""Sentiment: {sentiment}
Urgency Level: {urgency}
Key Concerns: {', '.join(concerns)}
Recommended Action: {action} response"""
            
            return {
                "analysis": analysis,
                "confidence": 0.7,  # Fixed confidence for rule-based analysis
                "model_used": "rule_based_analyzer",
                "sentiment": sentiment,
                "urgency": urgency,
                "concerns": concerns,
                "recommended_action": action
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze ticket sentiment: {e}")
            return None
    
    async def generate_ticket_insights(self, tickets: List[Ticket]) -> Optional[Dict[str, Any]]:
        """Generate insights from a collection of tickets using simple statistics."""
        try:
            await self.initialize()
            
            if not tickets:
                return None
            
            # Basic statistical analysis
            total_tickets = len(tickets)
            
            # Count by status
            status_counts = {}
            for ticket in tickets:
                status = ticket.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by priority
            priority_counts = {}
            for ticket in tickets:
                priority = ticket.priority.value
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Count by category
            category_counts = {}
            for ticket in tickets:
                category = ticket.category.value
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Find most common issues
            most_common_category = max(category_counts, key=category_counts.get)
            most_common_priority = max(priority_counts, key=priority_counts.get)
            
            # Generate insights text
            insights_text = f"""Analysis of {total_tickets} tickets:

1. Common Themes:
   - Most common category: {most_common_category} ({category_counts[most_common_category]} tickets)
   - Most common priority: {most_common_priority} ({priority_counts[most_common_priority]} tickets)

2. Status Distribution:
   {', '.join([f'{status}: {count}' for status, count in status_counts.items()])}

3. Priority Distribution:
   {', '.join([f'{priority}: {count}' for priority, count in priority_counts.items()])}

4. Category Distribution:
   {', '.join([f'{category}: {count}' for category, count in category_counts.items()])}

5. Recommendations:
   - Focus on {most_common_category} issues for process improvement
   - Consider dedicated resources for {most_common_priority} priority tickets
   - Monitor trends in ticket volume and resolution times"""
            
            return {
                "insights": insights_text,
                "analyzed_tickets": total_tickets,
                "sample_size": total_tickets,
                "generated_at": datetime.now().isoformat(),
                "statistics": {
                    "status_distribution": status_counts,
                    "priority_distribution": priority_counts,
                    "category_distribution": category_counts
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate ticket insights: {e}")
            return None

# Global instance
rag_service = SimpleRAGService()
