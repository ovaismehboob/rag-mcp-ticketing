"""
Semantic Kernel integration with MCP ticketing tools.
This module provides the main AI agent that can answer questions about tickets
using the MCP tools and Azure OpenAI.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
import json
from datetime import datetime

# Note: These imports will work once semantic-kernel is installed
try:
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatCompletion
    from semantic_kernel.contents import ChatHistory
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
    from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    SEMANTIC_KERNEL_AVAILABLE = False
    # Create mock classes for development without semantic-kernel
    class Kernel:
        def __init__(self): 
            self.services = {}
            self.plugins = {}
        def add_service(self, service): pass
        def add_plugin(self, plugin, name): pass
        async def invoke(self, *args, **kwargs): return None
    
    class ChatHistory:
        def __init__(self): 
            self.messages = []
        def add_user_message(self, message): 
            self.messages.append({"role": "user", "content": message})
        def add_assistant_message(self, message): 
            self.messages.append({"role": "assistant", "content": message})
    
    def kernel_function(func): return func

from config import settings
from mcp_client import mcp_client

logger = logging.getLogger(__name__)

class TicketingPlugin:
    """
    Semantic Kernel plugin that provides ticketing functions via MCP.
    This plugin exposes MCP tools as Semantic Kernel functions.
    """
    
    def __init__(self):
        """Initialize the ticketing plugin."""
        self.mcp_client = mcp_client
        
    @kernel_function(
        description="Search for tickets using semantic search with natural language queries",
        name="search_tickets"
    )
    async def search_tickets(self, query: str, limit: int = 5) -> str:
        """Search for tickets using natural language."""
        try:
            result = await self.mcp_client.search_tickets(query, limit)
            
            if result.get("success") and result.get("tickets"):
                tickets = result["tickets"]
                summary = f"Found {len(tickets)} tickets matching '{query}':\n\n"
                
                for ticket in tickets:
                    summary += f"🎫 Ticket #{ticket['id']}: {ticket['title']}\n"
                    summary += f"   Priority: {ticket['priority']} | Status: {ticket['status']}\n"
                    summary += f"   Description: {ticket['description'][:100]}...\n"
                    summary += f"   Reporter: {ticket['reporter']}\n\n"
                
                return summary
            else:
                return f"No tickets found matching '{query}'"
                
        except Exception as e:
            logger.error(f"Error searching tickets: {e}")
            return f"Error searching tickets: {str(e)}"
    
    @kernel_function(
        description="Create a new support ticket",
        name="create_ticket"
    )
    async def create_ticket(self, title: str, description: str, priority: str = "medium", 
                          category: str = "other", reporter: str = "user@example.com") -> str:
        """Create a new support ticket."""
        try:
            result = await self.mcp_client.create_ticket(title, description, priority, category, reporter)
            
            # Handle nested response structure from MCP
            if result.get("success") and result.get("result", {}).get("success"):
                ticket_data = result["result"].get("data", {})
                return f"✅ Created ticket #{ticket_data.get('ticket_id')}: {ticket_data.get('title')}\nStatus: {ticket_data.get('status')}"
            else:
                error_msg = result.get("result", {}).get("error", "Unknown error")
                return f"❌ Failed to create ticket: {error_msg}"
                
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return f"Error creating ticket: {str(e)}"
    
    @kernel_function(
        description="Get details of a specific ticket by ID",
        name="get_ticket"
    )
    async def get_ticket(self, ticket_id: int) -> str:
        """Get details of a specific ticket."""
        try:
            result = await self.mcp_client.get_ticket(ticket_id)
            
            # Handle nested response structure from MCP
            if result.get("success") and result.get("result", {}).get("success"):
                ticket = result["result"].get("data", {})
                details = f"🎫 Ticket #{ticket['id']}: {ticket['title']}\n"
                details += f"Status: {ticket['status']}\n"
                details += f"Priority: {ticket['priority']}\n"
                details += f"Category: {ticket['category']}\n"
                details += f"Reporter: {ticket['reporter']}\n"
                if ticket.get('assignee'):
                    details += f"Assignee: {ticket['assignee']}\n"
                details += f"Created: {ticket['created_at']}\n"
                if ticket.get('updated_at'):
                    details += f"Updated: {ticket['updated_at']}\n"
                details += f"Description: {ticket['description']}\n"
                
                if ticket.get('tags'):
                    details += f"Tags: {', '.join(ticket['tags'])}\n"
                
                return details
            else:
                return f"❌ Ticket #{ticket_id} not found"
                
        except Exception as e:
            logger.error(f"Error getting ticket {ticket_id}: {e}")
            return f"Error getting ticket: {str(e)}"
    
    @kernel_function(
        description="List tickets with optional filtering",
        name="list_tickets"
    )
    async def list_tickets(self, limit: int = 10, status: str = None) -> str:
        """List tickets with optional filtering."""
        try:
            result = await self.mcp_client.list_tickets(limit, status)
            
            # Handle nested response structure from MCP
            if result.get("success") and result.get("result", {}).get("success"):
                tickets = result["result"].get("tickets", [])
                total_count = result["result"].get("total_count", 0)
                
                if tickets:
                    summary = f"📋 Found {len(tickets)} tickets"
                    if status:
                        summary += f" with status '{status}'"
                    summary += f" (Total: {total_count}):\n\n"
                    
                    for ticket in tickets:
                        summary += f"🎫 #{ticket['id']}: {ticket['title']}\n"
                        summary += f"   {ticket['priority']} priority | {ticket['status']}\n"
                        summary += f"   Reporter: {ticket['reporter']}\n\n"
                    
                    return summary
                else:
                    return "No tickets found"
            else:
                error_msg = result.get("result", {}).get("error", "Unknown error")
                return f"Error listing tickets: {error_msg}"
                
        except Exception as e:
            logger.error(f"Error listing tickets: {e}")
            return f"Error listing tickets: {str(e)}"
    
    @kernel_function(
        description="Update an existing ticket",
        name="update_ticket"
    )
    async def update_ticket(self, ticket_id: int, status: str = None, priority: str = None, 
                          assignee: str = None, description: str = None) -> str:
        """Update an existing ticket."""
        try:
            updates = {}
            if status:
                updates["status"] = status
            if priority:
                updates["priority"] = priority
            if assignee:
                updates["assignee"] = assignee
            if description:
                updates["description"] = description
            
            if not updates:
                return "No updates provided"
            
            result = await self.mcp_client.update_ticket(ticket_id, **updates)
            
            if result.get("success") and result.get("ticket"):
                ticket = result["ticket"]
                return f"✅ Updated ticket #{ticket['id']}: {ticket['title']}\nNew status: {ticket['status']}"
            else:
                return f"❌ Failed to update ticket #{ticket_id}"
                
        except Exception as e:
            logger.error(f"Error updating ticket {ticket_id}: {e}")
            return f"Error updating ticket: {str(e)}"
    
    @kernel_function(
        description="Get ticket analytics and insights",
        name="get_analytics"
    )
    async def get_analytics(self) -> str:
        """Get ticket analytics and insights."""
        try:
            result = await self.mcp_client.get_analytics()
            
            if result.get("success") and result.get("analytics"):
                analytics = result["analytics"]
                summary = f"📊 Ticket Analytics:\n"
                summary += f"Total Tickets: {analytics['total_tickets']}\n"
                summary += f"Open Tickets: {analytics['open_tickets']}\n"
                summary += f"Closed Tickets: {analytics['closed_tickets']}\n"
                summary += f"In Progress: {analytics['in_progress_tickets']}\n"
                summary += f"Average Resolution Time: {analytics.get('avg_resolution_time', 'N/A')}\n"
                
                if analytics.get('priority_distribution'):
                    summary += f"\nPriority Distribution:\n"
                    for priority, count in analytics['priority_distribution'].items():
                        summary += f"  {priority}: {count}\n"
                
                return summary
            else:
                return "No analytics data available"
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return f"Error getting analytics: {str(e)}"
    
    @kernel_function(
        description="Get AI-powered resolution suggestions for a ticket",
        name="suggest_resolution"
    )
    async def suggest_resolution(self, ticket_id: int) -> str:
        """Get resolution suggestions for a ticket."""
        try:
            result = await self.mcp_client.suggest_resolution(ticket_id)
            
            if result.get("success") and result.get("suggestion"):
                suggestion = result["suggestion"]
                return f"💡 Resolution Suggestions for Ticket #{ticket_id}:\n\n{suggestion}"
            else:
                return f"No resolution suggestions available for ticket #{ticket_id}"
                
        except Exception as e:
            logger.error(f"Error getting suggestions for ticket {ticket_id}: {e}")
            return f"Error getting suggestions: {str(e)}"

class SemanticKernelAgent:
    """
    Main AI agent that uses Semantic Kernel with Azure OpenAI and MCP tools.
    """
    
    def __init__(self):
        """Initialize the Semantic Kernel agent."""
        self.kernel = None
        self.chat_completion = None
        self.chat_history = ChatHistory()
        self.ticketing_plugin = TicketingPlugin()
        
    async def initialize(self):
        """Initialize the Semantic Kernel with Azure OpenAI and plugins."""
        try:
            if not SEMANTIC_KERNEL_AVAILABLE:
                logger.warning("Semantic Kernel not available - using mock implementation")
                self.kernel = Kernel()
                return
                
            # Create kernel
            self.kernel = Kernel()
            
            # Configure Azure OpenAI service
            if settings.azure_openai_endpoint and settings.azure_openai_api_key:
                self.chat_completion = AzureChatCompletion(
                    deployment_name=settings.azure_openai_deployment_name,
                    endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version,
                )
                self.kernel.add_service(self.chat_completion)
                logger.info("Initialized Azure OpenAI chat completion service")
            else:
                logger.error("Azure OpenAI configuration missing - please provide endpoint and API key")
                raise ValueError("Azure OpenAI configuration required")
            
            # Add the ticketing plugin
            self.kernel.add_plugin(self.ticketing_plugin, plugin_name="ticketing")
            logger.info("Added ticketing plugin to Semantic Kernel")
            
            # Initialize chat history with system message
            self.chat_history.add_system_message(self._get_system_message())
            
            logger.info("Semantic Kernel agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Semantic Kernel agent: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources."""
        pass
    
    def _get_system_message(self) -> str:
        """Get the system message for the AI agent."""
        return """You are an intelligent IT support assistant with access to a ticketing system.

You can help users with:
- Searching for existing tickets using natural language
- Creating new support tickets
- Getting details about specific tickets
- Updating ticket status and information
- Providing analytics and insights about tickets
- Suggesting resolutions for tickets

You have access to the following functions:
- search_tickets: Search tickets using natural language queries
- create_ticket: Create new support tickets
- get_ticket: Get details of specific tickets by ID
- list_tickets: List tickets with optional filtering
- update_ticket: Update existing tickets
- get_analytics: Get ticket statistics and insights
- suggest_resolution: Get AI-powered resolution suggestions

When users ask questions about tickets, use the appropriate functions to get current information.
Be helpful, professional, and provide clear, actionable responses.
Always verify ticket information by calling the appropriate functions rather than making assumptions."""
    
    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return an AI response using Semantic Kernel.
        """
        try:
            if not self.kernel:
                await self.initialize()
            
            # Add user message to history
            self.chat_history.add_user_message(user_message)
            
            if not SEMANTIC_KERNEL_AVAILABLE:
                # Mock response for development
                return f"Mock response to: {user_message}\n(Semantic Kernel not installed - install requirements.txt for full functionality)"
            
            # Configure function calling behavior
            function_choice_behavior = FunctionChoiceBehavior.Auto()
            
            # Get AI response
            response = await self.chat_completion.get_chat_message_contents(
                chat_history=self.chat_history,
                settings=self.chat_completion.get_prompt_execution_settings_class()(
                    max_tokens=settings.max_tokens,
                    temperature=settings.temperature,
                    function_choice_behavior=function_choice_behavior
                ),
                kernel=self.kernel
            )
            
            # Extract the response text
            if response and len(response) > 0:
                assistant_message = str(response[0])
                self.chat_history.add_assistant_message(assistant_message)
                return assistant_message
            else:
                return "I apologize, but I didn't receive a proper response. Please try again."
                
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    async def reset_conversation(self):
        """Reset the conversation history."""
        self.chat_history = ChatHistory()
        self.chat_history.add_system_message(self._get_system_message())
        logger.info("Conversation history reset")

# Global agent instance
semantic_agent = SemanticKernelAgent()
