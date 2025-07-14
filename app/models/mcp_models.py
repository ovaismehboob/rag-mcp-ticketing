"""
MCP (Model Context Protocol) specific models.
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum

class MCPToolParameterType(str, Enum):
    """MCP tool parameter types."""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"

class MCPToolParameter(BaseModel):
    """MCP tool parameter definition."""
    type: MCPToolParameterType
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    items: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None

class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, MCPToolParameter] = Field(default_factory=dict)

class MCPToolCall(BaseModel):
    """MCP tool call request."""
    tool_name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")

class MCPToolResponse(BaseModel):
    """MCP tool call response."""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None

class MCPPrompt(BaseModel):
    """MCP prompt definition."""
    name: str = Field(..., description="Prompt name")
    description: str = Field(..., description="Prompt description")
    arguments: Optional[Dict[str, MCPToolParameter]] = None

class MCPServerInfo(BaseModel):
    """MCP server information."""
    name: str
    version: str
    description: str
    capabilities: List[str]
    tools: List[MCPTool]
    prompts: List[MCPPrompt]

class MCPListToolsResponse(BaseModel):
    """Response for listing MCP tools."""
    tools: List[MCPTool]

class MCPListPromptsResponse(BaseModel):
    """Response for listing MCP prompts."""
    prompts: List[MCPPrompt]
