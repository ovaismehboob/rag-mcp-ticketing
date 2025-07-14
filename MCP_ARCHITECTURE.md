# MCP Architecture Documentation

## Model Context Protocol (MCP) Implementation Guide

This document provides detailed technical documentation of the MCP implementation patterns used in the RAG-Based Ticketing System.

## 📐 MCP Architecture Patterns

### 1. MCP Server Architecture (Backend)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              MCP Server (Port 8000)                             │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           FastAPI Application Layer                         │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │ │
│  │  │   REST API      │  │   MCP Protocol  │  │   Health/Debug  │             │ │
│  │  │   Endpoints     │  │   Endpoints     │  │   Endpoints     │             │ │
│  │  │                 │  │                 │  │                 │             │ │
│  │  │ • /tickets/*    │  │ • /mcp/tools    │  │ • /health       │             │ │
│  │  │ • /docs         │  │ • /mcp/call_tool│  │ • /metrics      │             │ │
│  │  │ • /openapi.json │  │ • /mcp/server   │  │ • /debug        │             │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           SimpleMCPServer Layer                             │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │ │
│  │  │   Tool Registry │  │   Schema Mgmt   │  │   Request Mgmt  │             │ │
│  │  │                 │  │                 │  │                 │             │ │
│  │  │ • Tool Discovery│  │ • Input Schema  │  │ • Validation    │             │ │
│  │  │ • Function Map  │  │ • Output Schema │  │ • Error Handling│             │ │
│  │  │ • Metadata      │  │ • Type Safety   │  │ • Correlation   │             │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           Business Logic Layer                              │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │ │
│  │  │ Ticket Service  │  │ Vector Service  │  │Analytics Service│             │ │
│  │  │                 │  │                 │  │                 │             │ │
│  │  │ • CRUD Ops      │  │ • Embeddings    │  │ • Metrics       │             │ │
│  │  │ • Validation    │  │ • Similarity    │  │ • Trends        │             │ │
│  │  │ • State Mgmt    │  │ • RAG Search    │  │ • Insights      │             │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              Data Layer                                     │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │ │
│  │  │ SQLAlchemy ORM  │  │  Vector Store   │  │   Cache Layer   │             │ │
│  │  │                 │  │                 │  │                 │             │ │
│  │  │ • Models        │  │ • Embeddings    │  │ • Redis Cache   │             │ │
│  │  │ • Migrations    │  │ • Indexes       │  │ • Query Cache   │             │ │
│  │  │ • Relationships │  │ • Similarity    │  │ • Session Cache │             │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2. MCP Client Architecture (Frontend)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              MCP Client (Port 8001)                             │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                            Web Interface Layer                              │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │ │
│  │  │  Chat Interface │  │  Status Page    │  │  Admin Panel    │             │ │
│  │  │                 │  │                 │  │                 │             │ │
│  │  │ • Real-time UI  │  │ • Tool Status   │  │ • Reset Conv    │             │ │
│  │  │ • Bootstrap 5   │  │ • Health Check  │  │ • Debug Info    │             │ │
│  │  │ • Responsive    │  │ • Metrics       │  │ • Logs View     │             │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         Semantic Kernel Layer                               │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │ │
│  │  │   AI Kernel     │  │  Plugin System  │  │ Chat Management │             │ │
│  │  │                 │  │                 │  │                 │             │ │
│  │  │ • Azure OpenAI  │  │ • Tool Mapping  │  │ • History       │             │ │
│  │  │ • Function Call │  │ • Schema Map    │  │ • Context       │             │ │
│  │  │ • Prompt Exec   │  │ • Dynamic Load  │  │ • State Mgmt    │             │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                            MCP Client Layer                                 │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │ │
│  │  │Tool Discovery   │  │Protocol Handler │  │Connection Mgmt  │             │ │
│  │  │                 │  │                 │  │                 │             │ │
│  │  │ • Tool List     │  │ • HTTP Client   │  │ • Reconnection  │             │ │
│  │  │ • Schema Parse  │  │ • JSON-RPC      │  │ • Timeout       │             │ │
│  │  │ • Function Map  │  │ • Error Parse   │  │ • Health Check  │             │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 MCP Protocol Flow Diagrams

### 1. Tool Discovery Flow

```
┌─────────────┐    1. GET /mcp/tools    ┌─────────────┐
│             │────────────────────────▶│             │
│ MCP Client  │                        │ MCP Server  │
│             │◄────────────────────────│             │
└─────────────┘   2. Tool List JSON     └─────────────┘
       │                                       │
       ▼                                       ▼
┌─────────────┐                        ┌─────────────┐
│Schema Parse │                        │Tool Registry│
│& Mapping    │                        │& Metadata   │
└─────────────┘                        └─────────────┘
       │
       ▼
┌─────────────┐
│ SK Function │
│Registration │
└─────────────┘
```

### 2. Function Execution Flow

```
┌─────────────┐  1. User Query  ┌─────────────┐
│             │◄────────────────│             │
│   User      │                │  Web UI     │
│             │────────────────▶│             │
└─────────────┘  2. Response    └─────────────┘
                                       │
                                       ▼
┌─────────────┐ 3. Chat Request ┌─────────────┐
│             │◄────────────────│             │
│Semantic     │                │FastAPI App  │
│Kernel Agent │────────────────▶│             │
└─────────────┘ 8. Final Reply  └─────────────┘
       │
       ▼ 4. AI Processing
┌─────────────┐
│Azure OpenAI │ 5. Function Calling Decision
│GPT-3.5-Turbo│
└─────────────┘
       │
       ▼ 6. Tool Call
┌─────────────┐  7. HTTP POST   ┌─────────────┐
│             │ /mcp/call_tool  │             │
│ MCP Client  │────────────────▶│ MCP Server  │
│             │◄────────────────│             │
└─────────────┘  Tool Result    └─────────────┘
```

### 3. End-to-End Message Flow

```
User Input: "Create a ticket for network issues"
    │
    ▼
Web Interface (Port 8001)
    │ POST /chat
    ▼
Semantic Kernel Agent
    │ Chat processing
    ▼
Azure OpenAI API
    │ Function calling decision
    ▼ 
{
  "tool_calls": [{
    "function": {
      "name": "create_ticket",
      "arguments": {
        "title": "Network Issues",
        "description": "User experiencing network connectivity problems"
      }
    }
  }]
}
    │
    ▼
MCP Client (Internal)
    │ POST /mcp/call_tool
    ▼
MCP Server (Port 8000)
    │ Tool execution
    ▼
Business Logic → Database
    │ Success response
    ▼
{
  "success": true,
  "result": {
    "ticket_id": 123,
    "status": "open",
    "created_at": "2025-07-13T10:30:00Z"
  }
}
    │
    ▼
Azure OpenAI API (Final response)
    │ Natural language response
    ▼
"✅ I've created ticket #123 for your network issues. The ticket is now open and assigned to the IT support team."
    │
    ▼
Web Interface → User
```

## 🏗️ MCP Design Patterns

### 1. Tool Registration Pattern

```python
# Server-side tool registration
@mcp_server.tool()
async def create_ticket(
    title: str,
    description: str,
    priority: str = "medium"
) -> Dict[str, Any]:
    """Create a new support ticket"""
    
    # Input validation
    if not title or not description:
        raise ValueError("Title and description required")
    
    # Business logic
    ticket = await ticket_service.create_ticket({
        "title": title,
        "description": description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.utcnow()
    })
    
    # Structured response
    return {
        "success": True,
        "result": {
            "ticket_id": ticket.id,
            "title": ticket.title,
            "status": ticket.status
        }
    }
```

### 2. Client Discovery Pattern

```python
# Client-side tool discovery
class MCPClient:
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available MCP tools from server"""
        
        response = await self.http_client.get(f"{self.server_url}/mcp/tools")
        tools = response.json()
        
        # Cache tools for performance
        self.available_tools = tools
        
        # Register with Semantic Kernel
        for tool in tools:
            await self.register_sk_function(tool)
        
        return tools
    
    async def register_sk_function(self, tool: Dict[str, Any]):
        """Register MCP tool as Semantic Kernel function"""
        
        @kernel_function(
            description=tool["description"],
            name=tool["name"]
        )
        async def dynamic_function(**kwargs) -> str:
            return await self.call_tool(tool["name"], kwargs)
        
        # Add to plugin
        self.plugin.add_function(dynamic_function)
```

### 3. Error Handling Pattern

```python
# Standardized error handling
class MCPErrorHandler:
    @staticmethod
    async def handle_tool_error(
        tool_name: str,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle MCP tool execution errors"""
        
        # Log error with context
        logger.error(
            f"Tool '{tool_name}' failed",
            extra={
                "tool_name": tool_name,
                "error": str(error),
                "context": context,
                "correlation_id": context.get("correlation_id")
            }
        )
        
        # Return structured error
        return {
            "success": False,
            "error": {
                "type": error.__class__.__name__,
                "message": str(error),
                "tool": tool_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
```

### 4. Schema Validation Pattern

```python
# Input/Output schema validation
class ToolSchemaValidator:
    @staticmethod
    def validate_input(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool input against schema"""
        
        schema = TOOL_SCHEMAS.get(tool_name)
        if not schema:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Pydantic validation
        try:
            validated = schema.model_validate(arguments)
            return validated.model_dump()
        except ValidationError as e:
            raise ValueError(f"Invalid arguments: {e}")
    
    @staticmethod
    def validate_output(tool_name: str, result: Any) -> Dict[str, Any]:
        """Validate tool output format"""
        
        # Ensure consistent response structure
        if not isinstance(result, dict):
            result = {"data": result}
        
        if "success" not in result:
            result["success"] = True
        
        if "timestamp" not in result:
            result["timestamp"] = datetime.utcnow().isoformat()
        
        return result
```

## 📊 MCP Performance Optimization

### 1. Caching Strategy

```python
# Multi-level caching for MCP operations
class MCPCache:
    def __init__(self):
        self.tool_cache = TTLCache(maxsize=100, ttl=300)  # 5 min
        self.result_cache = TTLCache(maxsize=1000, ttl=60)  # 1 min
        self.schema_cache = {}  # Permanent
    
    async def get_tools(self, server_url: str) -> List[Dict[str, Any]]:
        """Cached tool discovery"""
        
        cache_key = f"tools:{server_url}"
        
        if cache_key in self.tool_cache:
            return self.tool_cache[cache_key]
        
        tools = await self._fetch_tools(server_url)
        self.tool_cache[cache_key] = tools
        return tools
    
    async def cache_result(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """Cache tool execution results"""
        
        # Create cache key from tool name and args
        args_hash = hashlib.md5(
            json.dumps(arguments, sort_keys=True).encode()
        ).hexdigest()
        
        cache_key = f"result:{tool_name}:{args_hash}"
        self.result_cache[cache_key] = result
```

### 2. Connection Pooling

```python
# HTTP connection pooling for MCP client
class MCPConnectionManager:
    def __init__(self):
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=20,  # Total connection pool size
                limit_per_host=10,  # Per-host limit
                keepalive_timeout=30,
                enable_cleanup_closed=True
            ),
            timeout=aiohttp.ClientTimeout(total=30)
        )
    
    async def call_tool(
        self,
        server_url: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make tool call with connection pooling"""
        
        async with self.session.post(
            f"{server_url}/mcp/call_tool",
            json={
                "name": tool_name,
                "arguments": arguments
            }
        ) as response:
            return await response.json()
```

### 3. Async Processing

```python
# Async tool execution with concurrency control
class AsyncMCPExecutor:
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_tools_parallel(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute multiple tools concurrently"""
        
        async def execute_single(tool_call):
            async with self.semaphore:
                return await self.call_tool(
                    tool_call["name"],
                    tool_call["arguments"]
                )
        
        # Execute all tools concurrently
        tasks = [execute_single(call) for call in tool_calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
```

## 🔐 MCP Security Patterns

### 1. Authentication & Authorization

```python
# MCP security middleware
class MCPSecurityMiddleware:
    async def authenticate_request(
        self,
        request: Request
    ) -> Optional[str]:
        """Authenticate MCP client requests"""
        
        # API Key authentication
        api_key = request.headers.get("Authorization")
        if not api_key or not api_key.startswith("Bearer "):
            raise HTTPException(401, "Missing or invalid API key")
        
        token = api_key.replace("Bearer ", "")
        
        # Validate token
        if not await self.validate_token(token):
            raise HTTPException(401, "Invalid API key")
        
        return self.get_client_id(token)
    
    async def authorize_tool(
        self,
        client_id: str,
        tool_name: str
    ) -> bool:
        """Check if client can access specific tool"""
        
        permissions = await self.get_client_permissions(client_id)
        return tool_name in permissions.get("allowed_tools", [])
```

### 2. Input Sanitization

```python
# Input sanitization for MCP tools
class MCPInputSanitizer:
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string inputs"""
        
        # Trim whitespace
        value = value.strip()
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
        
        # Remove potentially dangerous characters
        value = re.sub(r'[<>"\']', '', value)
        
        # HTML escape
        value = html.escape(value)
        
        return value
    
    @staticmethod
    def sanitize_arguments(
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sanitize all tool arguments"""
        
        sanitized = {}
        
        for key, value in arguments.items():
            if isinstance(value, str):
                sanitized[key] = MCPInputSanitizer.sanitize_string(value)
            elif isinstance(value, (int, float)):
                # Validate numeric ranges
                sanitized[key] = max(min(value, 1000000), -1000000)
            else:
                sanitized[key] = value
        
        return sanitized
```

## 📈 MCP Monitoring & Observability

### 1. Metrics Collection

```python
# MCP metrics collection
class MCPMetrics:
    def __init__(self):
        self.tool_calls = Counter()
        self.tool_duration = defaultdict(list)
        self.tool_errors = Counter()
    
    def record_tool_call(
        self,
        tool_name: str,
        duration: float,
        success: bool
    ):
        """Record tool execution metrics"""
        
        self.tool_calls[tool_name] += 1
        self.tool_duration[tool_name].append(duration)
        
        if not success:
            self.tool_errors[tool_name] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        
        return {
            "total_calls": sum(self.tool_calls.values()),
            "tools": {
                name: {
                    "calls": count,
                    "avg_duration": np.mean(self.tool_duration[name]),
                    "errors": self.tool_errors[name],
                    "success_rate": (
                        (count - self.tool_errors[name]) / count
                        if count > 0 else 0
                    )
                }
                for name, count in self.tool_calls.items()
            }
        }
```

### 2. Distributed Tracing

```python
# OpenTelemetry integration for MCP
from opentelemetry import trace

class MCPTracing:
    def __init__(self):
        self.tracer = trace.get_tracer("mcp-server")
    
    async def trace_tool_execution(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        client_id: str
    ):
        """Trace tool execution with context"""
        
        with self.tracer.start_as_current_span(
            f"mcp.tool.{tool_name}"
        ) as span:
            
            # Add span attributes
            span.set_attribute("mcp.tool.name", tool_name)
            span.set_attribute("mcp.client.id", client_id)
            span.set_attribute("mcp.args.count", len(arguments))
            
            try:
                # Execute tool
                result = await self.execute_tool(tool_name, arguments)
                
                span.set_attribute("mcp.success", True)
                span.set_status(trace.Status(trace.StatusCode.OK))
                
                return result
                
            except Exception as e:
                span.set_attribute("mcp.success", False)
                span.set_attribute("mcp.error", str(e))
                span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR,
                        str(e)
                    )
                )
                raise
```

## 🔄 MCP Extension Patterns

### 1. Plugin Architecture

```python
# Extensible MCP plugin system
class MCPPlugin:
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
    
    def tool(self, description: str = None):
        """Decorator for registering plugin tools"""
        
        def decorator(func):
            tool_name = f"{self.name}.{func.__name__}"
            
            self.tools[tool_name] = {
                "function": func,
                "description": description or func.__doc__,
                "schema": self._generate_schema(func)
            }
            
            return func
        
        return decorator
    
    def _generate_schema(self, func) -> Dict[str, Any]:
        """Generate JSON schema from function signature"""
        
        sig = inspect.signature(func)
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                properties[param_name] = {
                    "type": self._python_type_to_json_type(param.annotation)
                }
                
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

# Example plugin usage
analytics_plugin = MCPPlugin("analytics")

@analytics_plugin.tool("Get ticket trends over time")
async def get_ticket_trends(
    days: int = 30,
    group_by: str = "day"
) -> Dict[str, Any]:
    """Analyze ticket trends"""
    # Implementation
    pass
```

### 2. Dynamic Tool Loading

```python
# Dynamic tool loading system
class DynamicMCPLoader:
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self.loaded_plugins = {}
    
    async def load_plugin(self, plugin_path: str):
        """Dynamically load MCP plugin"""
        
        # Import plugin module
        spec = importlib.util.spec_from_file_location(
            "dynamic_plugin",
            plugin_path
        )
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        
        # Register plugin tools
        if hasattr(plugin_module, "MCP_PLUGIN"):
            plugin = plugin_module.MCP_PLUGIN
            
            for tool_name, tool_config in plugin.tools.items():
                await self.register_tool(tool_name, tool_config)
            
            self.loaded_plugins[plugin.name] = plugin
    
    async def register_tool(
        self,
        tool_name: str,
        tool_config: Dict[str, Any]
    ):
        """Register dynamically loaded tool"""
        
        async def tool_wrapper(**kwargs):
            return await tool_config["function"](**kwargs)
        
        # Add to MCP server
        self.mcp_server.add_tool(
            tool_name,
            tool_wrapper,
            tool_config["description"],
            tool_config["schema"]
        )
```

This comprehensive MCP architecture documentation provides detailed insights into the Model Context Protocol implementation patterns used in the RAG-Based Ticketing System, covering server architecture, client architecture, protocol flows, design patterns, performance optimization, security, monitoring, and extensibility patterns.
