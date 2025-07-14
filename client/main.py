"""
Main FastAPI application for the Semantic Kernel MCP Client.
This serves as the web interface for interacting with the ticketing system
through Semantic Kernel and Azure OpenAI.
"""
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from config import settings
from semantic_agent import semantic_agent
from mcp_client import mcp_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Web client for interacting with tickets using Semantic Kernel and Azure OpenAI",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Setup templates and static files
templates_dir = Path(__file__).parent / settings.template_dir
static_dir = Path(__file__).parent / settings.static_dir

# Create directories if they don't exist
static_dir.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(templates_dir))
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    success: bool = True

class StatusResponse(BaseModel):
    mcp_server_connected: bool
    semantic_kernel_ready: bool
    azure_openai_configured: bool
    timestamp: str

# Global state
app_state = {
    "initialized": False,
    "mcp_connected": False,
    "semantic_kernel_ready": False
}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Semantic Kernel MCP Client...")
    
    try:
        # Initialize the Semantic Kernel agent
        await semantic_agent.initialize()
        app_state["semantic_kernel_ready"] = True
        logger.info("Semantic Kernel agent initialized successfully")
        
        # Test MCP connection
        try:
            tools = await mcp_client.get_available_tools()
            app_state["mcp_connected"] = True
            logger.info(f"Connected to MCP server with {len(tools.get('tools', []))} tools")
        except Exception as e:
            logger.warning(f"MCP server connection failed: {e}")
            app_state["mcp_connected"] = False
        
        app_state["initialized"] = True
        logger.info("Client application startup complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        app_state["initialized"] = False

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Semantic Kernel MCP Client...")
    try:
        await semantic_agent.cleanup()
        logger.info("MCP agent cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat interface."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": settings.app_name
    })

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message through Semantic Kernel and return AI response.
    """
    try:
        logger.info(f"Processing chat message: {request.message[:100]}...")
        
        if not app_state["semantic_kernel_ready"]:
            raise HTTPException(
                status_code=503, 
                detail="Semantic Kernel agent not ready. Please check configuration."
            )
        
        # Process message through Semantic Kernel
        response = await semantic_agent.chat(request.message)
        
        logger.info("Chat response generated successfully")
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat(),
            success=True
        )
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get the current status of all services."""
    try:
        # Check MCP connection
        mcp_connected = False
        try:
            await mcp_client.get_available_tools()
            mcp_connected = True
        except Exception:
            mcp_connected = False
        
        # Check Azure OpenAI configuration
        azure_openai_configured = bool(
            settings.azure_openai_endpoint and 
            (settings.azure_openai_api_key or settings.use_managed_identity)
        )
        
        return StatusResponse(
            mcp_server_connected=mcp_connected,
            semantic_kernel_ready=app_state["semantic_kernel_ready"],
            azure_openai_configured=azure_openai_configured,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_conversation():
    """Reset the conversation history."""
    try:
        await semantic_agent.reset_conversation()
        logger.info("Conversation history reset")
        return {"success": True, "message": "Conversation reset successfully"}
        
    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "services": {
            "mcp_server": app_state["mcp_connected"],
            "semantic_kernel": app_state["semantic_kernel_ready"],
            "initialized": app_state["initialized"]
        }
    }

@app.get("/tools")
async def get_available_tools():
    """Get list of available MCP tools."""
    try:
        tools = await mcp_client.get_available_tools()
        return tools
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
