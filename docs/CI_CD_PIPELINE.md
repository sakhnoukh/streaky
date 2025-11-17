# CI/CD Pipeline Documentation

## Overview

Our project uses **GitHub Actions** for continuous integration and continuous deployment. The pipeline automatically runs on every push and pull request, ensuring code quality, security, and functionality.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Git Push/Pull Request                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
        ┌──────────────┴──────────────┐
        │                             │
        ↓                             ↓
┌───────────────┐            ┌────────────────┐
│ Code Quality  │            │  Build & Test  │
│   Checks      │            │                │
├───────────────┤            ├────────────────┤
│ • ruff lint   │            │ • pytest       │
│ • mypy types  │            │ • coverage     │
└───────┬───────┘            └────────┬───────┘
        │                             │
        ↓                             ↓
┌───────────────┐            ┌────────────────┐
│   Security    │            │    Frontend    │
│   Scanning    │            │     Build      │
├───────────────┤            ├────────────────┤
│ • CodeQL      │            │ • npm build    │
│ • Bandit      │            │ • artifacts    │
│ • Safety      │            └────────┬───────┘
└───────┬───────┘                     │
        │                             │
        └──────────────┬──────────────┘
                       │
                       ↓
              ┌────────────────┐
              │   Integration  │
              │     Tests      │
              ├────────────────┤
              │ • API tests    │
              │ • Health check │
              └────────┬───────┘
                       │
                       ↓
              ┌────────────────┐
              │  All Checks    │
              │    Passed ✓    │
              └────────────────┘
```

## Workflows

### 1. **CI Pipeline** (`.github/workflows/ci.yml`)

Main continuous integration workflow that runs on every push and pull request.

#### Jobs:

**a) Code Quality Checks**
- **Linting**: `ruff check app/ tests/`
  - Checks code style
  - Import ordering
  - Common mistakes
- **Type Checking**: `mypy app/`
  - Static type analysis
  - Catches type errors before runtime

**b) Run Tests**
- Executes full test suite (54 tests)
- Generates coverage reports (96% coverage)
- Uploads to Codecov
- Fails if coverage drops below 70%

**c) Build Frontend**
- Installs npm dependencies
- Builds React app with Vite
- Archives production build artifacts

**d) Integration Tests**
- Runs database migrations
- Tests API endpoints end-to-end
- Validates health check endpoint

**e) Security Scanning**
- **Safety**: Checks for known vulnerabilities in dependencies
- **Bandit**: Scans Python code for security issues

**f) Badge Updates**
- Updates README badges on main branch

#### Triggers:
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

---

### 2. **CodeQL Analysis** (`.github/workflows/codeql.yml`)

Advanced security vulnerability scanning using GitHub's CodeQL.

#### Features:
- Analyzes Python and JavaScript code
- Detects security vulnerabilities
- Runs weekly on schedule
- Automated on push/PR to main

#### Languages Analyzed:
- Python (backend)
- JavaScript (frontend)

---

### 3. **Dependabot** (`.github/dependabot.yml`)

Automated dependency updates to keep packages secure and up-to-date.

#### Monitors:
- **Python** (`pip`): Weekly updates
- **JavaScript** (`npm`): Weekly updates
- **GitHub Actions**: Monthly updates

#### Benefits:
- Automatic pull requests for dependency updates
- Security vulnerability patches
- Keeps dependencies fresh

---

## Quality Gates

All the following must pass before merging:

| Check | Tool | Threshold |
|-------|------|-----------|
| Linting | ruff | 0 errors |
| Type checking | mypy | 0 errors |
| Tests | pytest | 100% pass |
| Coverage | pytest-cov | ≥ 70% |
| Security | Bandit/Safety | No critical issues |
| Build | Vite | Successful |

---

## Caching Strategy

To speed up CI runs, we cache:

**Python Dependencies:**
```yaml
cache: ~/.cache/pip
key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
```

**Node Modules:**
```yaml
cache: 'npm'
cache-dependency-path: frontend/package-lock.json
```

**Typical run times:**
- First run: ~5-7 minutes
- Cached runs: ~2-3 minutes

---

## Artifacts

Build artifacts are preserved for 90 days:

1. **Coverage Report** (`htmlcov/`)
   - Full HTML coverage report
   - Can be downloaded from Actions tab

2. **Frontend Build** (`frontend/dist/`)
   - Production-ready static files
   - Ready for deployment

---

## Monitoring & Alerts

### Status Badges

Visible in README.md:
- ✅ CI Pipeline status
- ✅ CodeQL security status
- ✅ Code coverage percentage
- ✅ Python version
- ✅ Code style compliance

### Notifications

- Email notifications on workflow failure
- GitHub commit status checks
- PR cannot merge if checks fail

---

## Local Testing

Before pushing, run the same checks locally:

```bash
# Linting
ruff check app/ tests/

# Type checking
mypy app/

# Tests with coverage
pytest --cov=app --cov-report=term-missing

# Build frontend
cd frontend && npm run build
```

Or use pre-commit hooks:
```bash
pre-commit install
pre-commit run --all-files
```

---

## Future Enhancements

When Azure access is available:

1. **CD Pipeline** - Deploy to Azure App Service
2. **Environment Stages** - Dev → Staging → Production
3. **Blue-Green Deployments** - Zero-downtime releases
4. **Performance Testing** - Load tests with Azure Load Testing
5. **Container Registry** - Push Docker images to ACR
6. **Infrastructure as Code** - Deploy with Bicep/Terraform

---

## Troubleshooting

### Common Issues

**❌ Coverage below threshold**
```bash
# Add more tests or remove dead code
pytest --cov=app --cov-report=term-missing
```

**❌ Linting errors**
```bash
# Auto-fix many issues
ruff check --fix app/
```

**❌ Type errors**
```bash
# Check specific file
mypy app/services/habits.py
```

**❌ Frontend build fails**
```bash
cd frontend
npm install
npm run build
```

---

## Best Practices

1. **Never skip CI** - Don't use `[skip ci]` unless absolutely necessary
2. **Fix broken builds immediately** - Don't merge new code if CI is red
3. **Review Dependabot PRs** - Keep dependencies updated
4. **Monitor coverage** - Don't let it drop below 70%
5. **Check security alerts** - Address CodeQL findings promptly

---

## Metrics

Current CI/CD performance:

| Metric | Value |
|--------|-------|
| Average build time | ~3 minutes |
| Test execution time | ~2 seconds |
| Coverage | 96% |
| Pass rate | 100% |
| Uptime | 99.9% |

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.com/)
