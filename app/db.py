from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Use computed database URL (Azure SQL if configured, else SQLite)
SQLALCHEMY_DATABASE_URL = settings.database_url_computed

# Create engine with appropriate settings based on database type
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Azure SQL / PostgreSQL configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=settings.is_development  # Log SQL in development
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Function to create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
