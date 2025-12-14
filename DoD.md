# Definition of Done (DoD)

A user story, task, or feature is considered **DONE** when ALL of the following criteria are met:

## Code Quality

- [ ] Code is written and follows project coding standards
- [ ] Linting passes (`ruff check app/ tests/`)
- [ ] Type checking passes (`mypy app/`)
- [ ] No new linting warnings introduced

## Testing

- [ ] All unit tests pass (`pytest tests/unit/`)
- [ ] All API tests pass (`pytest tests/api/`)
- [ ] Code coverage is at least 70% for new code (`pytest --cov=app --cov-fail-under=70`)
- [ ] Edge cases and error handling are tested

## Review

- [ ] Pull Request created with descriptive title and description
- [ ] Code reviewed and approved by at least 1 team member
- [ ] PR linked to corresponding user story or issue

## Documentation

- [ ] Code includes appropriate docstrings and comments
- [ ] README or API docs updated if public interfaces changed
- [ ] CHANGELOG updated for user-facing changes

## Deployment

- [ ] CI pipeline passes (all GitHub Actions green)
- [ ] Feature deployed to staging environment (if applicable)
- [ ] Health checks pass after deployment
- [ ] No critical bugs or regressions introduced

## Acceptance

- [ ] Acceptance criteria from user story are satisfied
- [ ] Product Owner has reviewed and accepted the feature
