# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-17

### Added
- **Core Features**
  - Habit creation with daily and weekly goal types
  - Idempotent entry logging
  - Current and best streak calculation
  - Statistics endpoints for 7-day and 30-day windows
  - Health check endpoint

- **Architecture**
  - Hexagonal architecture (ports & adapters) implementation
  - Repository pattern with protocol-based interfaces
  - Strategy pattern for goal policies (DailyPolicy, WeeklyPolicy)
  - Service layer for business logic orchestration
  - Clean separation of concerns (routers, services, repositories)

- **Authentication & Security**
  - JWT-based authentication with OAuth2 password flow
  - Protected endpoints with bearer token validation
  - Request ID middleware for request tracking
  - Timing middleware for performance monitoring

- **Data Layer**
  - SQLAlchemy ORM with SQLite (development)
  - Alembic database migrations
  - User, Habit, and Entry models with proper relationships
  - Unique constraints for habit names per user and entries per habit/date

- **Developer Experience**
  - Comprehensive test suite (96% coverage)
  - Unit tests for utils, policies, and services
  - API integration tests with TestClient
  - Type checking with mypy (100% pass rate)
  - Code linting with ruff
  - Pre-commit hooks configuration
  - pyproject.toml for tool configuration

- **Documentation**
  - Comprehensive README with curl examples
  - API documentation via Swagger UI and ReDoc
  - Contributing guidelines
  - Pull request template

### Technical Details
- Python 3.13+
- FastAPI web framework
- SQLAlchemy 2.0 with declarative mapping
- Pydantic v2 for validation and settings
- pytest with coverage reporting
- ruff for linting, mypy for type checking
