# Streaky - Habit Tracker API

[![CI Pipeline](https://github.com/sakhnoukh/streaky/actions/workflows/ci.yml/badge.svg)](https://github.com/sakhnoukh/streaky/actions/workflows/ci.yml)
[![CodeQL](https://github.com/sakhnoukh/streaky/actions/workflows/codeql.yml/badge.svg)](https://github.com/sakhnoukh/streaky/actions/workflows/codeql.yml)
[![codecov](https://codecov.io/gh/sakhnoukh/streaky/branch/main/graph/badge.svg)](https://codecov.io/gh/sakhnoukh/streaky)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A clean, testable FastAPI service for tracking daily and weekly habits with streak calculation. Built with hexagonal architecture (ports & adapters), following SOLID principles and design patterns.

## Features

- ✅ Create and manage habits (daily or weekly goals)
- ✅ Log habit entries with idempotent operations
- ✅ Track current and best streaks
- ✅ Get statistics for 7-day or 30-day windows
- ✅ JWT authentication
- ✅ Structured logging with request IDs
- ✅ Comprehensive test suite (96% coverage)
- ✅ Type-checked with mypy
- ✅ Linted with ruff

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AZURE CLOUD                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐     ┌──────────────────────────────────────────────┐     │
│   │   GitHub     │     │           Azure App Service                  │     │
│   │   Actions    │────▶│           (streaky-api)                      │     │
│   │   CI/CD      │     │    ┌─────────────────────────────────┐      │     │
│   └──────────────┘     │    │         FastAPI App             │      │     │
│                        │    │  ┌───────────┐ ┌─────────────┐  │      │     │
│                        │    │  │  Routers  │ │  Services   │  │      │     │
│   ┌──────────────┐     │    │  │  (HTTP)   │ │ (Business)  │  │      │     │
│   │   React      │     │    │  └─────┬─────┘ └──────┬──────┘  │      │     │
│   │   Frontend   │────▶│    │        │              │         │      │     │
│   │   (Static)   │     │    │  ┌─────▼──────────────▼─────┐   │      │     │
│   └──────────────┘     │    │  │     Repositories         │   │      │     │
│                        │    │  │     (Data Access)        │   │      │     │
│                        │    │  └───────────┬──────────────┘   │      │     │
│                        │    └──────────────┼──────────────────┘      │     │
│                        └───────────────────┼─────────────────────────┘     │
│                                            │                                │
│                                            ▼                                │
│                        ┌──────────────────────────────────────┐            │
│                        │         Azure SQL Database           │            │
│                        │         (streaky-db)                 │            │
│                        └──────────────────────────────────────┘            │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │                    Application Insights                          │     │
│   │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │     │
│   │   │  Logs    │  │ Metrics  │  │  Alerts  │  │Dashboard │        │     │
│   │   └──────────┘  └──────────┘  └──────────┘  └──────────┘        │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Hexagonal Architecture (Ports & Adapters)

```
                 ┌─────────────────────────────────────┐
    HTTP Request │         FastAPI Routers             │
    ────────────▶│         (HTTP Adapters)             │
                 └─────────────┬───────────────────────┘
                               │
                               ▼
                 ┌─────────────────────────────────────┐
                 │         Service Layer               │
                 │    (Business Logic / Use Cases)     │◀── Strategy Pattern
                 │                                     │    (Goal Policies)
                 └─────────────┬───────────────────────┘
                               │
                               ▼
                 ┌─────────────────────────────────────┐
                 │      Repository Protocols           │
                 │           (Ports)                   │
                 └─────────────┬───────────────────────┘
                               │
                               ▼
                 ┌─────────────────────────────────────┐
                 │    SQLAlchemy Repositories          │
                 │        (DB Adapters)                │
                 └─────────────┬───────────────────────┘
                               │
                               ▼
                          ┌─────────┐
                          │   DB    │
                          └─────────┘
```

**Key Principles:**
- **Domain Layer**: Pure business logic (services, policies, utils)
- **Ports**: Repository protocols defining interfaces
- **Adapters**: SQLAlchemy repositories, FastAPI routers
- **Patterns**: Strategy (goal policies), Repository, Factory, Decorator

## Quick Start

### Prerequisites
- Python 3.13+
- pip

### Installation

```bash
# 1. Clone and navigate to project
cd streaky

# 2. Create virtual environment
python -m venv .env
source .env/bin/activate  # On Windows: .env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 4. Set up environment variables
cp .env.example .env

# 5. Run database migrations
.env/bin/python -m alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload --port 8002
```

The API will be available at `http://localhost:8002`
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## Authentication

All habit endpoints require JWT authentication. First, obtain a token:

```bash
# Get access token (hardcoded for development: testuser/testpass)
curl -X POST http://localhost:8002/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"

# Response:
# {"access_token":"eyJ...","token_type":"bearer"}
```

**⚠️ Note**: The current implementation uses hardcoded credentials for development. Production deployment requires proper user authentication with password hashing and database storage.

## API Examples

### 1. Health Check

```bash
curl http://localhost:8002/healthz
# {"ok":true}
```

### 2. Create a Habit

```bash
# Set your token
TOKEN="your_access_token_here"

# Create a daily habit
curl -X POST http://localhost:8002/habits \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Morning Exercise",
    "goal_type": "daily"
  }'

# Response:
# {"id":1,"name":"Morning Exercise","goal_type":"daily"}

# Create a weekly habit
curl -X POST http://localhost:8002/habits \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Review",
    "goal_type": "weekly"
  }'
```

**Error Cases**:
- `409 Conflict`: Habit name already exists for this user
- `400 Bad Request`: Invalid goal_type (must be "daily" or "weekly")
- `401 Unauthorized`: Missing or invalid token

### 3. List Habits with Streaks

```bash
curl http://localhost:8002/habits \
  -H "Authorization: Bearer $TOKEN"

# Response:
# [
#   {
#     "id": 1,
#     "name": "Morning Exercise",
#     "goal_type": "daily",
#     "streak": 5
#   }
# ]
```

### 4. Log an Entry

```bash
# Log entry for today (idempotent - can call multiple times)
curl -X POST http://localhost:8002/habits/1/entries \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-11-17"
  }'

# Response:
# {"ok":true}
```

**Error Cases**:
- `404 Not Found`: Habit with given ID doesn't exist

### 5. Get Habit Statistics

```bash
# Get 7-day statistics
curl "http://localhost:8002/habits/1/stats?range=7d" \
  -H "Authorization: Bearer $TOKEN"

# Response:
# {
#   "habit_id": 1,
#   "current_streak": 5,
#   "best_streak": 5,
#   "days": [
#     {"date": "2024-11-11", "done": false},
#     {"date": "2024-11-12", "done": false},
#     {"date": "2024-11-13", "done": true},
#     {"date": "2024-11-14", "done": true},
#     {"date": "2024-11-15", "done": true},
#     {"date": "2024-11-16", "done": true},
#     {"date": "2024-11-17", "done": true}
#   ]
# }

# Get 30-day statistics
curl "http://localhost:8002/habits/1/stats?range=30d" \
  -H "Authorization: Bearer $TOKEN"
```

## Development

### Run Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_streak.py

# Run with coverage report
pytest --cov=app --cov-report=term-missing
```

### Code Quality

```bash
# Lint code
ruff check app/

# Fix linting issues automatically
ruff check --fix app/

# Type check
mypy app/

# Run all quality checks
ruff check app/ && mypy app/ && pytest
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Database Migrations

```bash
# Create a new migration
.env/bin/python -m alembic revision --autogenerate -m "description"

# Apply migrations
.env/bin/python -m alembic upgrade head

# Rollback one migration
.env/bin/python -m alembic downgrade -1

# View migration history
.env/bin/python -m alembic history
```

## Project Structure

```
streaky/
├── app/
│   ├── main.py              # FastAPI app factory & DI wiring
│   ├── config.py            # Pydantic settings
│   ├── db.py                # SQLAlchemy setup
│   ├── logging.py           # Middleware (request_id, timing)
│   ├── models.py            # ORM entities
│   ├── schemas.py           # Pydantic I/O models
│   ├── dependencies.py      # FastAPI dependencies
│   ├── utils/
│   │   └── streak.py        # Pure streak calculations
│   ├── policies/
│   │   └── goal.py          # Strategy pattern implementations
│   ├── repositories/
│   │   ├── base.py          # Repository protocols (ports)
│   │   ├── habits.py        # SQLAlchemy habit repository
│   │   └── entries.py       # SQLAlchemy entry repository
│   ├── services/
│   │   └── habits.py        # Business logic orchestration
│   └── routers/
│       ├── auth.py          # Authentication endpoints
│       └── habits.py        # Habit endpoints
├── tests/
│   ├── unit/                # Unit tests (utils, policies, services)
│   └── api/                 # API tests with TestClient
├── alembic/                 # Database migrations
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml           # Tool configurations
├── .pre-commit-config.yaml  # Pre-commit hooks
└── README.md                # This file
```

## Design Patterns

1. **Strategy Pattern**: Goal policies (DailyPolicy, WeeklyPolicy) allow adding new goal types without modifying existing code
2. **Repository Pattern**: Abstracts data access through protocols/interfaces
3. **Factory Pattern**: Database session and service creation
4. **Decorator Pattern**: Logging middleware for cross-cutting concerns

## SOLID Principles

- **S**ingle Responsibility: Routers handle HTTP, services handle business logic, repositories handle persistence
- **O**pen/Closed: Extend behavior via new strategies without modifying existing code
- **L**iskov Substitution**: Any repository implementation can substitute another
- **I**nterface Segregation: Separate HabitRepository and EntryRepository protocols
- **D**ependency Inversion: Services depend on repository abstractions (protocols)

## Frontend UI

A React-based web interface is available in the `frontend/` directory.

### Quick Start

```bash
# Terminal 1: Start backend
uvicorn app.main:app --reload --port 8002

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

Access the UI at **http://localhost:5000**

**Features:**
- Login with JWT authentication
- Create and manage habits
- Log daily entries
- View current streaks
- Beautiful, responsive design

See [`frontend/README.md`](frontend/README.md) for details.

## Configuration

Environment variables (`.env`):

```bash
DATABASE_URL=sqlite:///./streaky.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and guidelines.

## Azure Deployment

### Live Endpoints

| Service | URL |
|---------|-----|
| **API** | https://streaky-api.azurewebsites.net |
| **Health Check** | https://streaky-api.azurewebsites.net/health |
| **API Documentation** | https://streaky-api.azurewebsites.net/docs |

### Azure Resources

| Resource | Type | Location |
|----------|------|----------|
| `streaky-api` | App Service | Canada Central |
| `streaky-sql-server/streaky-db` | SQL Database | East US |
| `Streaky-insights` | Application Insights | West Europe |
| `BCSAI2025-DEVOPS-STUDENT-1B` | Resource Group | - |

### CI/CD Pipeline

- **GitHub Actions**: Automated testing on push/PR
- **Azure Pipelines**: Build → Test → Deploy to Azure App Service
- **Deployment**: Automatic on merge to `main` branch

### Monitoring

See [docs/MONITORING.md](docs/MONITORING.md) for:
- Application Insights dashboard setup
- KQL queries for uptime, response time, error rate
- Alert configuration

## License

MIT License

