"""
Main FastAPI application for the RAG-based ticketing system with MCP support.
Follows Azure best practices for API development and error handling.
"""
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from .config import settings
from .routers import tickets_router, mcp_router
from .services import ticket_service, vector_store, rag_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with proper initialization and cleanup."""
    logger.info("Starting up ticketing API with MCP support...")
    
    try:
        # Initialize services with proper error handling
        logger.info("Initializing ticket service...")
        await ticket_service.initialize()
        
        logger.info("Initializing vector store...")
        await vector_store.initialize()
        
        logger.info("Initializing RAG service...")
        await rag_service.initialize()
        
        logger.info("All services initialized successfully")
        
        # Store initialization status in app state
        app.state.initialized = True
        app.state.startup_time = time.time()
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        app.state.initialized = False
        raise
    
    finally:
        # Cleanup resources
        logger.info("Shutting down ticketing API...")
        # Add any cleanup logic here if needed

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    RAG-based Ticketing System with Model Context Protocol (MCP) Support
    
    This API provides both traditional REST endpoints and MCP-compatible tools
    for incident ticket management with AI-powered features:
    
    * **Ticket Management**: Create, read, update, delete incident tickets
    * **Semantic Search**: AI-powered search using vector embeddings
    * **RAG Integration**: Retrieval-Augmented Generation for intelligent responses
    * **MCP Compatibility**: Works with Semantic Kernel MCPPlugin
    * **Analytics**: Ticket insights and performance metrics
    
    ## MCP Integration
    
    The `/mcp` endpoints expose tools that can be consumed by MCP clients:
    - **Tools**: Ticket management functions exposed as MCP tools
    - **Semantic Search**: Vector-based search with similarity scoring
    - **AI Insights**: GPT-powered analysis and recommendations
    
    ## Authentication
    
    This demo version uses basic authentication. In production, integrate with
    Azure AD, managed identities, and proper RBAC.
    """,
    debug=settings.debug,
    lifespan=lifespan
)

# Configure CORS with security considerations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.url} "
            f"in {process_time:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url} in {process_time:.3f}s - {e}")
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with proper logging."""
    logger.error(f"Unhandled exception for {request.method} {request.url}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

# Include routers
app.include_router(tickets_router)
app.include_router(mcp_router)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the RAG-based Ticketing API with MCP Support",
        "version": settings.app_version,
        "docs_url": "/docs",
        "mcp_tools_url": "/mcp/tools",
        "mcp_info_url": "/mcp/info",
        "health_url": "/health",
        "features": [
            "Incident ticket management",
            "Semantic search with vector embeddings", 
            "RAG-powered AI insights",
            "Model Context Protocol (MCP) support",
            "Semantic Kernel integration ready",
            "Real-time analytics and reporting"
        ]
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint with service status."""
    try:
        # Check if app was initialized properly
        if not getattr(app.state, "initialized", False):
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": "Services not initialized"
                }
            )
        
        # Check individual services
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime_seconds": time.time() - getattr(app.state, "startup_time", time.time()),
            "version": settings.app_version,
            "services": {}
        }
        
        # Check ticket service
        try:
            await ticket_service.initialize()
            health_status["services"]["ticket_service"] = "healthy"
        except Exception as e:
            health_status["services"]["ticket_service"] = f"unhealthy: {e}"
            health_status["status"] = "degraded"
        
        # Check vector store
        try:
            await vector_store.initialize()
            vector_stats = await vector_store.get_collection_stats()
            health_status["services"]["vector_store"] = {
                "status": "healthy",
                "stats": vector_stats
            }
        except Exception as e:
            health_status["services"]["vector_store"] = f"unhealthy: {e}"
            health_status["status"] = "degraded"
        
        # Check RAG service
        try:
            await rag_service.initialize()
            health_status["services"]["rag_service"] = "healthy"
        except Exception as e:
            health_status["services"]["rag_service"] = f"unhealthy: {e}"
            health_status["status"] = "degraded"
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        
        return JSONResponse(
            status_code=status_code,
            content=health_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

# Custom OpenAPI schema for better MCP documentation
def custom_openapi():
    """Custom OpenAPI schema with MCP-specific documentation."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add MCP-specific tags and documentation
    openapi_schema["tags"] = [
        {
            "name": "tickets",
            "description": "Traditional REST API for ticket management"
        },
        {
            "name": "mcp", 
            "description": "Model Context Protocol endpoints for Semantic Kernel integration"
        },
        {
            "name": "health",
            "description": "Health check and monitoring endpoints"
        },
        {
            "name": "root",
            "description": "Root API information"
        }
    ]
    
    # Add MCP-specific info
    openapi_schema["info"]["x-mcp-capabilities"] = [
        "tools",
        "prompts",
        "semantic_search", 
        "ai_insights"
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Application entry point
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )
