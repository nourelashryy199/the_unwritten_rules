
# Engineering Standards

## 1. Purpose

This document defines the coding, testing, dependency,
configuration, and security conventions for The Unwritten Rules.

The objective is to maintain a readable, testable, extensible
codebase without introducing unnecessary complexity.

Standards apply to new code. Existing code will be brought
into alignment incrementally when appropriate.

## 2. General Principles

- Prefer clarity over cleverness.
- Follow SOLID principles where they improve the design.
- Keep modules focused on one coherent responsibility.
- Avoid duplicating business logic.
- Introduce abstractions when there is a concrete need.
- Prefer composition over inheritance.
- Keep external integrations outside the domain layer.
- Document non-obvious architectural decisions.
- Do not introduce infrastructure before it is needed.

## 3. Python Coding Conventions

### 3.1 Formatting

- Follow PEP 8.
- Use four spaces for indentation.
- Use descriptive snake_case names for functions and variables.
- Use PascalCase for classes.
- Use UPPER_SNAKE_CASE for constants.
- Prefer a maximum line length of 88 characters.
- Keep imports organised.

Ruff will be used for linting and formatting.

### 3.2 Type Annotations

All new public functions and methods should declare
parameter and return types.

Example:

```python
def calculate_score(
    similarity: float,
    context_weight: float,
) -> float:
    return similarity * context_weight
```

Prefer explicit domain types over unstructured dictionaries
when the structure is stable.

Use Pydantic models for validated data structures.

Use `None` explicitly when a value may be absent.

Avoid `Any` unless its use is justified.

### 3.3 Exceptions

- Raise meaningful exceptions for invalid operations.
- Do not silently suppress errors.
- Do not expose internal exception details through API responses.
- Handle expected errors at the appropriate architectural boundary.
- Avoid broad exception handlers unless necessary for cleanup
  or boundary-level error translation.

### 3.4 Logging

- Use Python's logging facilities.
- Do not use print statements for production diagnostics.
- Never log passwords, tokens, or other secrets.
- Avoid logging contributor narratives or sensitive contextual
  details unless there is a specific, justified operational need.
- Include useful diagnostic information without exposing
  personal data.

## 4. Dependency Management

- Maintain Python dependencies in backend/pyproject.toml.
- Use a virtual environment for local development.
- Do not import infrastructure implementations into domain code.
- Prefer well-maintained dependencies.
- Avoid adding libraries for trivial functionality.
- Review dependency changes before committing them.

## 5. Testing Standards

pytest is the backend testing framework.

### 5.1 Test Organisation

- Store backend tests in backend/tests/.
- Name test files test_*.py.
- Name test functions test_*.
- Keep tests independent and deterministic.
- Use fixtures for reusable setup when they reduce duplication.

### 5.2 Unit Tests

Unit tests should cover:

- Expected behaviour
- Invalid inputs
- Boundary conditions
- Missing and unknown information
- Domain invariants
- Failure scenarios

Domain unit tests should not require:
- A running database
- Network access
- External LLM APIs
- Cloud services

### 5.3 Integration Tests

Integration tests will verify interactions between components.

Examples:
- API and application services
- Application services and repositories
- Database persistence
- Vector search
- Embedding integration

External integrations should be tested separately from
pure domain logic.

### 5.4 Regression Tests

When fixing a bug:

1. Add a test reproducing the failure.
2. Implement the correction.
3. Verify the test passes.
4. Run the relevant existing tests.

### 5.5 Test Execution

From the repository root:

```bash
python -m pytest -v
```

All tests must pass before merging changes.

## 6. Frontend Standards

The frontend will use React and TypeScript.

Conventions:

- Prefer functional components.
- Use TypeScript types for component props.
- Separate API communication from presentation components.
- Avoid embedding business rules directly in UI components.
- Keep reusable components focused.
- Handle loading, empty, and error states explicitly.
- Avoid premature introduction of complex state management.

Frontend testing tools will be selected when frontend
implementation begins.

## 7. Configuration Management

Environment-specific configuration must be separate
from application business logic.

Examples:

- Database connection URL
- Embedding model identifier
- LLM provider configuration
- API host and port
- Logging level

Configuration should be read through a dedicated
configuration module rather than scattered environment
variable accesses throughout the codebase.

Defaults may be provided for non-sensitive development
settings.

Required configuration must be validated at startup.

## 8. Secrets Management

Secrets must never be committed to Git.

Examples:

- API keys
- Database passwords
- Access tokens
- Cloud credentials

Conventions:

- Use environment variables for local and deployed secrets.
- Keep local .env files out of version control.
- Provide .env.example with placeholder values only.
- Do not hardcode secrets in source code.
- Do not include secrets in logs or error messages.
- Use the deployment platform's secret-management
  mechanism in production.

Secret rotation and production access policies will be
defined when deployment infrastructure is introduced.

## 9. Git and Version Control

- Use meaningful commit messages.
- Keep commits focused on coherent changes.
- Avoid committing generated caches and virtual environments.
- Review git diff before committing.
- Do not commit failing tests.
- Do not commit local configuration containing secrets.

Suggested commit prefixes:

- feat: new functionality
- fix: bug correction
- test: tests
- docs: documentation
- refactor: structural improvement without behaviour change
- chore: maintenance or tooling

## 10. Dependency Boundaries

The intended dependency direction is:

API -> Application -> Domain

Infrastructure provides implementations of interfaces
required by application services.

Rules:

- Domain must not import API or infrastructure modules.
- Application services must not depend directly on concrete
  database or LLM implementations.
- API routes should delegate use cases to application services.
- Infrastructure code should not contain core business rules.
- Dependency injection should be introduced where it solves
  a real dependency-management problem.

## 11. Continuous Integration

GitHub Actions will eventually automate:

- Dependency installation
- Formatting checks
- Linting
- Automated tests
- Build verification

The initial CI pipeline should remain small.

Additional checks will be introduced when justified
by project requirements.

CI implementation belongs to US-026.

## 12. Definition of Done

A user story may be marked Done only when:

1. Every acceptance criterion has been checked.
2. Required implementation is complete.
3. Relevant tests pass.
4. Documentation is updated where necessary.
5. Architectural boundaries are respected.
6. No known blocking defects remain.
7. Changes are committed and pushed.
8. The GitHub issue and project board reflect the result.

Passing tests alone does not establish completion
if acceptance criteria remain unmet.

## 13. Review and Evolution

These standards are intended to evolve as the project grows.

Changes should be justified by concrete engineering needs.

New conventions should not be introduced solely to imitate
large production systems.

Architectural consistency and maintainability take
priority over unnecessary abstraction.
