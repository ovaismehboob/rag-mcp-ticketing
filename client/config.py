"""
Configuration settings for the Semantic Kernel MCP Client.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class ClientSettings(BaseSettings):
    """Client configuration settings."""
    
    # App settings
    app_name: str = "Semantic Kernel MCP Client"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8001
    
    # MCP Server connection
    mcp_server_url: str = "http://127.0.0.1:8000"
    mcp_server_timeout: int = 30
    
    # Azure OpenAI settings - will be populated from Azure Key Vault or environment
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_deployment_name: str = "gpt-35-turbo"
    azure_openai_model_name: str = "gpt-3.5-turbo"
    
    # Azure Key Vault settings (optional)
    azure_keyvault_url: Optional[str] = None
    use_managed_identity: bool = True
    
    # Semantic Kernel settings
    semantic_kernel_log_level: str = "INFO"
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # Web interface settings
    template_dir: str = "templates"
    static_dir: str = "static"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load from environment variables
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Global settings instance
settings = ClientSettings()
