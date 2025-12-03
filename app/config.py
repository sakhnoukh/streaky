from pydantic_settings import BaseSettings
from typing import Literal, Optional


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    VERSION: str = "1.0.0"
    
    # Database - SQLite (local) or Azure SQL (cloud)
    DATABASE_URL: str = "sqlite:///./streaky.db"
    
    # Azure SQL (optional - if provided, overrides DATABASE_URL)
    AZURE_SQL_SERVER: Optional[str] = None
    AZURE_SQL_DATABASE: str = "streaky-db"
    AZURE_SQL_USERNAME: Optional[str] = None
    AZURE_SQL_PASSWORD: Optional[str] = None
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application Insights
    APPINSIGHTS_INSTRUMENTATION_KEY: Optional[str] = None
    APPINSIGHTS_CONNECTION_STRING: Optional[str] = None
    
    # Azure Key Vault (optional)
    AZURE_KEY_VAULT_URL: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5000,http://localhost:5001,http://localhost:5002,http://localhost:5003,http://localhost:5004,http://localhost:5005,http://127.0.0.1:5000,http://127.0.0.1:5002,https://streakyfelix.z6.web.core.windows.net"
    
    @property
    def database_url_computed(self) -> str:
        """Return Azure SQL URL if configured, otherwise SQLite"""
        if self.AZURE_SQL_SERVER and self.AZURE_SQL_USERNAME and self.AZURE_SQL_PASSWORD:
            # Azure SQL connection string using pymssql (no ODBC driver needed)
            return (
                f"mssql+pymssql://{self.AZURE_SQL_USERNAME}:{self.AZURE_SQL_PASSWORD}"
                f"@{self.AZURE_SQL_SERVER}/{self.AZURE_SQL_DATABASE}"
            )
        return self.DATABASE_URL
    
    @property
    def cors_origins(self) -> list:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    class Config:
        env_file = ".env"


settings = Settings()
