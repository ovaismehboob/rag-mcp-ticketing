"""
Semantic Kernel integration with MCP ticketing tools using MCPSsePlugin.
This module provides the main AI agent that uses the proper Semantic Kernel MCPSsePlugin
to connect to the MCP server and automatically register all available tools.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Note: These imports will work once semantic-kernel[mcp] is installed
try:
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
    from semantic_kernel.connectors.mcp import MCPSsePlugin
    from semantic_kernel.contents import ChatHistory
    from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
    SEMANTIC_KERNEL_MCP_AVAILABLE = True
except ImportError as e:
    SEMANTIC_KERNEL_MCP_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Semantic Kernel MCP not available: {e}")
    
    # Create mock classes for development without semantic-kernel[mcp]
    class Kernel:
        def __init__(self): 
            self.services = {}
            self.plugins = {}
        def add_service(self, service): pass
        def add_plugin(self, plugin, name=None): pass
        async def invoke(self, *args, **kwargs): return None
    
    class ChatHistory:
        def __init__(self): 
            self.messages = []
        def add_user_message(self, message): 
            self.messages.append({"role": "user", "content": message})
        def add_assistant_message(self, message): 
            self.messages.append({"role": "assistant", "content": message})
        def add_system_message(self, message):
            self.messages.append({"role": "system", "content": message})
    
    class MCPSsePlugin:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass

from config import settings

logger = logging.getLogger(__name__)

class SemanticKernelMCPAgent:
    """
    Main AI agent that uses Semantic Kernel with Azure OpenAI and MCPSsePlugin.
    This implementation follows the official Microsoft documentation for MCP integration.
    """
    
    def __init__(self):
        """Initialize the Semantic Kernel MCP agent."""
        self.kernel = None
        self.chat_completion = None
        self.chat_history = ChatHistory()
        self.mcp_plugin = None
        self._plugin_context = None
        
    async def initialize(self):
        """Initialize the Semantic Kernel with Azure OpenAI and MCP plugin."""
        try:
            if not SEMANTIC_KERNEL_MCP_AVAILABLE:
                logger.warning("Semantic Kernel MCP not available - using mock implementation")
                logger.warning("Install with: pip install semantic-kernel[mcp]")
                self.kernel = Kernel()
                return
            
            # Initialize MCP SSE Plugin
            self.mcp_plugin = MCPSsePlugin(
                name="Ticketing",
                description="AI-powered ticketing system with RAG capabilities",
                url=settings.mcp_server_url,
                load_tools=True,
                load_prompts=False,  # Our server doesn't provide prompts
                request_timeout=settings.mcp_server_timeout
            )
            
            # Use async context manager to connect to MCP server
            self._plugin_context = await self.mcp_plugin.__aenter__()
            
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
            
            # Add the MCP plugin - this automatically discovers and registers all MCP tools
            self.kernel.add_plugin(self.mcp_plugin)
            logger.info("Added MCP plugin to Semantic Kernel - tools auto-discovered")
            
            # Initialize chat history with system message
            self.chat_history.add_system_message(self._get_system_message())
            
            logger.info("Semantic Kernel MCP agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Semantic Kernel MCP agent: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources including MCP connection."""
        try:
            if self._plugin_context and hasattr(self.mcp_plugin, '__aexit__'):
                await self.mcp_plugin.__aexit__(None, None, None)
                logger.info("MCP plugin connection closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _get_system_message(self) -> str:
        """Get the system message for the AI agent."""
        return """You are an intelligent IT support assistant with access to a ticketing system via Model Context Protocol (MCP).

You have access to the following capabilities through MCP tools:
- Creating new support tickets with detailed information
- Searching for existing tickets using natural language queries
- Retrieving specific ticket details by ID
- Listing tickets with optional filtering
- Updating ticket status, assignments, and information
- Getting analytics and insights about ticket trends
- Providing AI-powered resolution suggestions

The system uses RAG (Retrieval-Augmented Generation) for semantic search, meaning you can:
- Search tickets using natural language descriptions
- Find similar tickets based on content similarity
- Get contextual insights from historical ticket data

When users ask questions about tickets, always use the appropriate MCP tools to get current, accurate information.
Be helpful, professional, and provide clear, actionable responses.

Key guidelines:
- Always verify information by calling MCP tools rather than making assumptions
- When creating tickets, gather all necessary details from the user
- For searches, use descriptive queries to get the best semantic matching
- Provide ticket IDs and relevant details in your responses
- Suggest appropriate actions based on ticket status and content"""
    
    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return an AI response using Semantic Kernel with MCP.
        """
        try:
            if not self.kernel:
                await self.initialize()
            
            # Add user message to history
            self.chat_history.add_user_message(user_message)
            
            if not SEMANTIC_KERNEL_MCP_AVAILABLE:
                # Mock response for development
                return f"Mock MCP response to: {user_message}\n(Semantic Kernel MCP not installed - install with: pip install semantic-kernel[mcp])"
            
            # Configure function calling behavior for MCP tools
            function_choice_behavior = FunctionChoiceBehavior.Auto()
            
            # Get AI response with automatic MCP tool usage
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
            logger.error(f"Error in MCP chat processing: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    

    
    async def reset_conversation(self):
        """Reset the conversation history."""
        self.chat_history = ChatHistory()
        self.chat_history.add_system_message(self._get_system_message())
        logger.info("Conversation history reset")

# Global agent instance
semantic_mcp_agent = SemanticKernelMCPAgent()
