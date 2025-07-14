"""
Configuration settings for the ticketing API.
Follows Azure best practices for configuration management.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class Settings(BaseSettings):
    """Application settings with Azure integration."""
    
    # Application settings
    app_name: str = "Ticketing API with MCP"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    database_url: str = "sqlite:///./tickets.db"
    
    # Vector store settings
    vector_db_path: str = "./vector_store"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Azure settings (following best practices)
    azure_client_id: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_keyvault_url: Optional[str] = None
    
    # AI/ML settings
    openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2023-12-01-preview"
    
    # MCP settings
    mcp_server_name: str = "ticketing-mcp-server"
    mcp_server_version: str = "1.0.0"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_azure_secrets()
    
    def _load_azure_secrets(self):
        """Load secrets from Azure Key Vault if configured."""
        if not self.azure_keyvault_url:
            return
        
        try:
            # Use managed identity for Azure-hosted apps
            credential = DefaultAzureCredential()
            client = SecretClient(
                vault_url=self.azure_keyvault_url,
                credential=credential
            )
            
            # Load secrets if they exist
            secrets_to_load = [
                ("openai-api-key", "openai_api_key"),
                ("database-url", "database_url"),
                ("secret-key", "secret_key")
            ]
            
            for secret_name, attr_name in secrets_to_load:
                try:
                    secret = client.get_secret(secret_name)
                    if secret.value:
                        setattr(self, attr_name, secret.value)
                except Exception as e:
                    # Log but don't fail - fall back to env vars
                    print(f"Warning: Could not load secret {secret_name}: {e}")
                    
        except Exception as e:
            print(f"Warning: Could not connect to Azure Key Vault: {e}")

# Global settings instance
settings = Settings()
