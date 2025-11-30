# Streaky - Scrum Artifacts & Process Documentation

## Team Information

| Role | Member |
|------|--------|
| Product Owner | (Rotating) |
| Scrum Master | (Rotating) |
| Developers | All team members |

## Definition of Done (DoD)

A user story/task is considered **DONE** when:

- [ ] Code is written and follows project coding standards
- [ ] All unit tests pass (`pytest tests/unit/`)
- [ ] All API tests pass (`pytest tests/api/`)
- [ ] Code coverage ≥ 70%
- [ ] Linting passes (`ruff check app/ tests/`)
- [ ] Type checking passes (`mypy app/`)
- [ ] Code has been reviewed by at least 1 team member
- [ ] Documentation updated (if applicable)
- [ ] Feature deployed to staging/production
- [ ] No known bugs related to the feature

---

## Product Backlog

### Epics

| Epic | Description | Priority |
|------|-------------|----------|
| **Core API** | Habit CRUD, entries, streaks | High |
| **Authentication** | User registration, JWT tokens | High |
| **Azure Infrastructure** | App Service, SQL DB, App Insights | High |
| **CI/CD Pipeline** | Automated build, test, deploy | High |
| **Monitoring** | Dashboards, alerts, logging | Medium |
| **Frontend** | React UI for habit tracking | Medium |

### User Stories

| ID | Story | Epic | Status | Sprint |
|----|-------|------|--------|--------|
| US-001 | As a user, I can create a new habit | Core API | ✅ Done | 1 |
| US-002 | As a user, I can log habit completion | Core API | ✅ Done | 1 |
| US-003 | As a user, I can view my habit streaks | Core API | ✅ Done | 1 |
| US-004 | As a user, I can see 7/30 day statistics | Core API | ✅ Done | 2 |
| US-005 | As a user, I can register and login | Auth | ✅ Done | 2 |
| US-006 | As a dev, the API is deployed on Azure | Infra | ✅ Done | 3 |
| US-007 | As a dev, code is auto-tested on PR | CI/CD | ✅ Done | 2 |
| US-008 | As a dev, I can see app metrics | Monitoring | ✅ Done | 3 |
| US-009 | As a user, I can use a web UI | Frontend | ✅ Done | 3 |
| US-010 | As a user, I can edit/delete habits | Core API | ✅ Done | 4 |

---

## Sprint History

### Sprint 0: Project Setup (Week 1)
**Goal**: Define MVP, set up project structure

**Completed:**
- ✅ Project scaffolding (FastAPI, SQLAlchemy)
- ✅ Development environment setup
- ✅ Initial backlog creation
- ✅ Architecture decisions (Hexagonal)

**Retrospective:**
- 👍 Good: Clear project vision established
- 👎 Improve: Need more detailed user stories
- 🔄 Action: Add acceptance criteria to all stories

---

### Sprint 1: Core Features (Week 2)
**Goal**: Implement basic habit tracking

**Sprint Backlog:**
| Task | Assignee | Status |
|------|----------|--------|
| Create Habit model & migration | Dev | ✅ |
| Implement HabitRepository | Dev | ✅ |
| Implement HabitService | Dev | ✅ |
| Create habits router | Dev | ✅ |
| Add streak calculation | Dev | ✅ |
| Write unit tests | Dev | ✅ |

**Velocity:** 18 story points

**Retrospective:**
- 👍 Good: TDD approach worked well
- 👍 Good: Repository pattern simplifies testing
- 👎 Improve: Need integration tests
- 🔄 Action: Add API tests with TestClient

---

### Sprint 2: Auth & CI/CD (Week 3)
**Goal**: Add authentication and automated pipeline

**Sprint Backlog:**
| Task | Assignee | Status |
|------|----------|--------|
| JWT authentication | Dev | ✅ |
| User registration endpoint | Dev | ✅ |
| GitHub Actions CI | Dev | ✅ |
| Azure Pipeline config | Dev | ✅ |
| API test suite | Dev | ✅ |

**Velocity:** 21 story points

**Retrospective:**
- 👍 Good: CI catches issues early
- 👍 Good: Auth implementation was smooth
- 👎 Improve: Test coverage could be higher
- 🔄 Action: Increase coverage to 70%+

---

### Sprint 3: Azure Deployment (Week 4)
**Goal**: Deploy to Azure with monitoring

**Sprint Backlog:**
| Task | Assignee | Status |
|------|----------|--------|
| Create Azure resources | Dev | ✅ |
| Configure App Service | Dev | ✅ |
| Set up SQL Database | Dev | ✅ |
| Application Insights | Dev | ✅ |
| Frontend deployment | Dev | ✅ |
| Health endpoints | Dev | ✅ |

**Velocity:** 24 story points

**Retrospective:**
- 👍 Good: Azure deployment successful
- 👍 Good: Monitoring provides visibility
- 👎 Improve: Database connection string management
- 🔄 Action: Use Azure Key Vault for secrets

---

### Sprint 4: Polish & Demo Prep (Week 5)
**Goal**: Final polish, documentation, demo preparation

**Sprint Backlog:**
| Task | Assignee | Status |
|------|----------|--------|
| Edit/Delete habits | Dev | ✅ |
| Architecture diagram | Dev | ✅ |
| Monitoring documentation | Dev | ✅ |
| Fix test issues | Dev | ✅ |
| Demo preparation | Team | 🔄 |

**Velocity:** TBD (sprint in progress)

---

## Burndown Chart (Sprint 4)

```
Story Points Remaining
│
30 ├─●
   │  ╲
25 ├───●
   │    ╲
20 ├─────●
   │      ╲
15 ├───────●
   │        ╲
10 ├─────────●
   │          ╲
 5 ├───────────●
   │            ╲
 0 ├─────────────●────────
   └──┬──┬──┬──┬──┬──┬──┬─▶
     M  T  W  Th F  S  Su   Days
```

---

## Metrics

### Code Quality
- **Test Coverage**: 77%
- **Linting**: ✅ Pass (ruff)
- **Type Checking**: ✅ Pass (mypy)

### Deployment
- **Build Success Rate**: 95%
- **Deployment Frequency**: On every merge to main
- **Mean Time to Recovery**: < 30 minutes

### API Performance
- **Average Response Time**: < 200ms
- **Availability**: 99%+ (target)
- **Error Rate**: < 1% (target)

---

## Meeting Notes Template

### Daily Standup
**Date**: ____

**What I did yesterday:**
- 

**What I will do today:**
- 

**Blockers:**
- 

### Sprint Review
**Sprint**: ____
**Date**: ____

**Demo Items:**
1. 
2. 

**Stakeholder Feedback:**
- 

### Sprint Retrospective
**Sprint**: ____

**What went well:**
- 

**What could be improved:**
- 

**Action items:**
- 

---

## Links

- **GitHub Repository**: https://github.com/sakhnoukh/streaky
- **Live API**: https://streaky-api.azurewebsites.net
- **API Docs**: https://streaky-api.azurewebsites.net/docs
- **Azure Portal**: [Resource Group](https://portal.azure.com/#resource/subscriptions/e0b9cada-61bc-4b5a-bd7a-52c606726b3b/resourceGroups/BCSAI2025-DEVOPS-STUDENT-1B)
