Streaky (Habit Tracker) — Design Doc (Non-Azure + DevOps, SOLID, Patterns)

Audience: WindSurf team
Goal: Build a clean, testable FastAPI service (SQLite locally) that’s production-ready once Azure access is granted. Include DevOps guardrails (quality gates, code workflow), SOLID, and well-chosen patterns.

1) Scope & Non-Goals
In scope (WindSurf)

FastAPI backend with domain/services/repos split.

SQLite + Alembic migrations.

Features: create habit, log entry (idempotent), list habits with current streak, stats (7/30d), healthz.

Validation, structured errors, logging & request IDs.

Tests (unit + API) with coverage target.

Dev workflow: pre-commit, ruff, mypy, pytest, conventional commits, PR templates.

Out of scope (kept for Azure team later)

Azure resources, pipelines, slots, App Insights wiring.

2) DevOps Guardrails (team workflow)

Branching: trunk-based. main protected; feature branches feat/<slug>.

Conventional Commits: feat:, fix:, refactor:, test:, docs:, chore:.

PR policy: 1 reviewer; all checks green; link issue; small, focused PRs (<300 LOC).

Quality gates: ruff + mypy clean, tests pass, coverage ≥70% (enforced in CI).

Test pyramid: heavy unit tests (utils/services), thinner API tests; no E2E yet.

Artifacts: README.md, API examples (curl), CONTRIBUTING.md, PR template, CHANGELOG.md (auto from commits later).

Definition of Done (DoD):

Acceptance criteria met

Tests + coverage gate pass

Lint/type-check pass

API documented in README examples

No TODOs without issue links

3) High-Level Architecture (Ports & Adapters with FastAPI)

We’ll use a hexagonal (ports & adapters) layout to keep domain logic independent from frameworks:

               +-----------------+
HTTP Router -> |  Service Layer  | <- uses Policies (Strategies)
               +-----------------+
                        |
                        v
               +-----------------+
               |  Repository(s)  |  (port: Repo interfaces)
               +-----------------+
                        |
                        v
                     SQLite


Ports (interfaces): repository protocols and policy interfaces.

Adapters: SQLAlchemy repositories (DB adapter), FastAPI router (HTTP adapter).

Benefits: adheres to SOLID (especially DIP), easy to swap DB later.

4) SOLID Commitments (concrete mapping)

S – Single Responsibility:

routers/*.py only HTTP translation.

services/*.py business rules (idempotency, streaks orchestration).

repositories/*.py persistence only.

utils/streak.py pure calculations.

O – Open/Closed:

Add new goal policies (e.g., weekly) via Strategy without touching existing logic.

New DB backends by adding a new adapter (repo implementation).

L – Liskov Substitution:

Service depends on Repo Protocols; any repo that satisfies contracts can be substituted.

I – Interface Segregation:

Split into HabitRepository and EntryRepository; clients depend only on what they use.

D – Dependency Inversion:

Services depend on abstract protocols (ports), injected via FastAPI dependencies or a small factory.

5) Design Patterns (and where we use them)

Strategy — Goal Policy & Streak computation

GoalPolicy interface with is_hit(dates, today) / window(days); implementations: DailyPolicy, WeeklyPolicy.

Allows adding MonthlyPolicy without changing services.

Repository — DB access abstraction

HabitRepository, EntryRepository define the port; SqlAlchemyHabitRepository is the adapter.

Factory — Session/Unit-of-Work factory

Create DB session via a factory (SessionLocal) to avoid hard dependency.

Decorator — Logging/Timing cross-cutting concerns

Optional: a @log_call decorator around service methods to produce structured logs.

(Optional) Template Method — Stats range

Shared stats steps with range-specific hooks if needed (may be overkill—strategy usually suffices).

6) Directory Layout
streaky/
  app/
    __init__.py
    main.py                # app factory, DI wiring, middleware
    config.py              # pydantic BaseSettings
    db.py                  # engine, SessionLocal, Base
    logging.py             # request_id + timing middleware, JSON logs
    models.py              # ORM entities
    schemas.py             # Pydantic I/O models
    utils/
      streak.py            # current_streak(), best_streak()
    policies/
      goal.py              # Strategy interfaces & implementations
    repositories/
      base.py              # Protocols (ports)
      habits.py            # SQLAlchemy adapters
      entries.py           # SQLAlchemy adapters
    services/
      habits.py            # orchestration/business rules
    routers/
      habits.py            # HTTP endpoints
  tests/
    unit/                  # utils, policies, services
    api/                   # router tests with TestClient
  alembic.ini
  alembic/
    versions/
  requirements.txt
  requirements-dev.txt
  .env.example
  .pre-commit-config.yaml
  README.md

7) Key Interfaces & Snippets
7.1 Repository Ports (Protocols)
# app/repositories/base.py
from typing import Protocol, Iterable
from datetime import date
from app.models import Habit, Entry

class HabitRepository(Protocol):
    def create(self, user_id: int, name: string, goal_type: str) -> Habit: ...
    def get(self, habit_id: int) -> Habit | None: ...
    def list_by_user(self, user_id: int) -> list[Habit]: ...
    def exists_name(self, user_id: int, name: str) -> bool: ...

class EntryRepository(Protocol):
    def exists_on(self, habit_id: int, d: date) -> bool: ...
    def create(self, habit_id: int, d: date) -> Entry: ...
    def dates_between(self, habit_id: int, start: date, end: date) -> Iterable[date]: ...

7.2 Strategy for Goal Policy
# app/policies/goal.py
from typing import Protocol, Iterable
from datetime import date, timedelta

class GoalPolicy(Protocol):
    def window(self, days: int, today: date) -> tuple[date, date]: ...
    def is_hit(self, dates: set[date], d: date) -> bool: ...

class DailyPolicy:
    def window(self, days: int, today: date): return today - timedelta(days=days-1), today
    def is_hit(self, dates: set[date], d: date): return d in dates

class WeeklyPolicy:
    def window(self, days: int, today: date): return today - timedelta(days=days-1), today
    def is_hit(self, dates: set[date], d: date): return d.isoweekday() in {1,2,3,4,5,6,7} and d in dates  # MVP placeholder

7.3 Streak Utils (pure)
# app/utils/streak.py
from datetime import date, timedelta
def current_streak(dates: set[date], today: date) -> int:
    if today not in dates: return 0
    streak, cur = 1, today
    while (cur := cur - timedelta(days=1)) in dates: streak += 1
    return streak

def best_streak(dates: set[date]) -> int:
    if not dates: return 0
    s, seen = 0, set(dates)
    for d in list(seen):
        if d - timedelta(days=1) not in seen:
            run, cur = 1, d
            while (cur := cur + timedelta(days=1)) in seen: run += 1
            s = max(s, run)
    return s

7.4 Service Orchestration (DIP)
# app/services/habits.py
from datetime import date
from typing import Literal
from app.repositories.base import HabitRepository, EntryRepository
from app.utils.streak import current_streak, best_streak
from app.policies.goal import DailyPolicy, WeeklyPolicy, GoalPolicy

Goal = Literal["daily","weekly"]
def _policy(goal: Goal) -> GoalPolicy:
    return DailyPolicy() if goal == "daily" else WeeklyPolicy()

class HabitService:
    def __init__(self, habits: HabitRepository, entries: EntryRepository):
        self.habits, self.entries = habits, entries

    def create(self, user_id: int, name: str, goal: Goal = "daily"):
        if self.habits.exists_name(user_id, name):
            raise ValueError("name_exists")
        return self.habits.create(user_id, name, goal)

    def log_today(self, habit_id: int, today: date):
        if not self.habits.get(habit_id): raise LookupError("not_found")
        if not self.entries.exists_on(habit_id, today):
            self.entries.create(habit_id, today)

    def list_with_streaks(self, user_id: int, today: date):
        out = []
        for h in self.habits.list_by_user(user_id):
            dates = set(self.entries.dates_between(h.id, today, today))
            out.append({"id": h.id, "name": h.name, "goal_type": h.goal_type,
                        "streak": current_streak(dates, today)})
        return out

    def stats(self, habit_id: int, days: int, today: date):
        h = self.habits.get(habit_id)
        if not h: raise LookupError("not_found")
        pol = _policy(h.goal_type)
        start, end = pol.window(days, today)
        ds = set(self.entries.dates_between(h.id, start, end))
        return {
            "habit_id": h.id,
            "current_streak": current_streak(ds, today),
            "best_streak": best_streak(ds),
            "days": [{"date": d.isoformat(), "done": pol.is_hit(ds, d)}
                     for d in (start + timedelta(n) for n in range((end-start).days+1))]
        }

8) API (FastAPI Routers)

POST /habits → create (409 if name exists)

GET /habits → list with current streak

POST /habits/{id}/entries → log today (idempotent 200)

GET /habits/{id}/stats?range=7d|30d → stats

GET /healthz → {ok:true}

Schemas in schemas.py; Problem+JSON error responses for 409, 404.

9) Persistence (SQLAlchemy) & Migrations (Alembic)

Models: user, habit (unique per user name), entry (unique(habit_id,date)).
Alembic: alembic revision --autogenerate -m "init tables" → alembic upgrade head.
Local default: DATABASE_URL=sqlite:///./streaky.db.

10) Observability (local)

JSON logs with fields: ts, level, request_id, route, status, duration_ms.

Middleware: request-id (UUID), timing.

Decorator (optional): @log_call for service methods (pattern: Decorator).

11) Testing

Unit:

utils/streak.py edge cases.

services/habits.py with fake repositories (in-memory) to assert business rules.

API:

FastAPI TestClient w/ temp SQLite. Covers routes, validation, idempotency.

Targets: coverage ≥70%, ruff + mypy clean.

12) Developer Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
pytest -q --cov=app


Pre-commit

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.8
    hooks: [ { id: ruff, args: ["--fix"] } ]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks: [ { id: mypy } ]

13) Deliverables Checklist (WindSurf)

 Project layout created (as above).

 Repository protocols & SQLAlchemy adapters implemented.

 Strategy policies (DailyPolicy, WeeklyPolicy stub) implemented.

 Services orchestrate rules (idempotent logging; streaks; stats).

 Routers with Pydantic schemas; Problem+JSON errors.

 Alembic init tables migration.

 Logging middleware & request IDs.

 Tests (unit + API) ≥70% coverage; ruff/mypy clean.

 README with run/test/migrate and curl examples.

 PR template + CONTRIBUTING (workflow & DoD).

14) Initial Issues (ready to create)

Scaffold project & configs (pre-commit, pyproject, env).

Models & migration (user, habit, entry, constraints).

Repo Protocols + SQLA adapters (ports/adapters).

Streak utils (unit tests).

Goal policies (Strategy) + tests.

HabitService methods + unit tests.

Routers + schemas + API tests.

Logging middleware (request_id, timing).

Docs & PR template.