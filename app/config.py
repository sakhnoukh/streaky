from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    VERSION: str = "1.0.0"
    
    # Database - SQLite (local) or Azure SQL (cloud)
    DATABASE_URL: str = "sqlite:///./streaky.db"
    
    # Azure SQL (optional - if provided, overrides DATABASE_URL)
    AZURE_SQL_SERVER: str | None = None
    AZURE_SQL_DATABASE: str = "streaky-db"
    AZURE_SQL_USERNAME: str | None = None
    AZURE_SQL_PASSWORD: str | None = None
    AZURE_SQL_DRIVER: str = "ODBC Driver 18 for SQL Server"
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application Insights
    APPINSIGHTS_INSTRUMENTATION_KEY: str | None = None
    APPINSIGHTS_CONNECTION_STRING: str | None = None
    
    # Azure Key Vault (optional)
    AZURE_KEY_VAULT_URL: str | None = None
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5000,http://localhost:5001,http://127.0.0.1:5000"
    
    @property
    def database_url_computed(self) -> str:
        """Return Azure SQL URL if configured, otherwise SQLite"""
        if self.AZURE_SQL_SERVER and self.AZURE_SQL_USERNAME and self.AZURE_SQL_PASSWORD:
            # Azure SQL connection string
            return (
                f"mssql+pyodbc://{self.AZURE_SQL_USERNAME}:{self.AZURE_SQL_PASSWORD}"
                f"@{self.AZURE_SQL_SERVER}/{self.AZURE_SQL_DATABASE}"
                f"?driver={self.AZURE_SQL_DRIVER.replace(' ', '+')}"
                f"&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
            )
        return self.DATABASE_URL
    
    @property
    def cors_origins(self) -> list[str]:
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
