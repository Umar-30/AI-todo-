# Research: Project Setup

**Feature**: 001-project-setup
**Date**: 2026-01-19
**Status**: Complete

## Technology Decisions

### 1. FastAPI Project Structure

**Decision**: Use standard FastAPI application structure with `src/` directory for source code.

**Rationale**:
- FastAPI recommends separating source code from configuration and tests
- `src/` pattern allows clean imports and package isolation
- Consistent with Python packaging best practices (PEP 517/518)

**Alternatives Considered**:
- Flat structure (all .py files in root) - Rejected: doesn't scale, import issues
- `app/` directory naming - Rejected: `src/` is more universal across languages

### 2. Database Driver Selection

**Decision**: Use `psycopg` (psycopg3) as the PostgreSQL driver.

**Rationale**:
- Native async support for FastAPI async endpoints
- Modern replacement for psycopg2 with better performance
- Full compatibility with SQLModel and SQLAlchemy 2.0
- Neon PostgreSQL officially recommends psycopg for serverless connections

**Alternatives Considered**:
- psycopg2 - Rejected: legacy, requires separate async wrapper
- asyncpg - Rejected: not compatible with SQLModel/SQLAlchemy without adapters

### 3. Environment Variable Management

**Decision**: Use `python-dotenv` for local development, standard environment variables in production.

**Rationale**:
- Simple, well-established pattern for 12-factor app configuration
- .env.example provides documentation for required variables
- Production systems can inject env vars without .env file dependency

**Alternatives Considered**:
- pydantic-settings - Considered for future: adds validation but overkill for setup phase
- Direct os.environ only - Rejected: poor developer experience for local setup

### 4. Virtual Environment Strategy

**Decision**: Use standard Python `venv` module, located at `backend/.venv/`.

**Rationale**:
- Built into Python, no additional tools required
- Consistent across platforms (Windows/Linux/macOS)
- IDE (VS Code, PyCharm) auto-detect .venv directories

**Alternatives Considered**:
- Poetry - Rejected: adds complexity for simple dependency management
- Conda - Rejected: heavy, not needed for pure Python project
- pipenv - Rejected: slower, less predictable than pip + venv

### 5. Health Check Endpoint Design

**Decision**: Single `/health` endpoint returning JSON with server and database status.

**Rationale**:
- Simple, standard pattern for container orchestration and load balancers
- Database connectivity check ensures end-to-end system health
- JSON response allows programmatic health monitoring

**Alternatives Considered**:
- Separate `/health` and `/ready` endpoints - Deferred: can add later if needed for k8s
- Plain text response - Rejected: JSON is more extensible and parseable

## Best Practices Applied

### FastAPI Application

1. **Lifespan context manager**: Use FastAPI's lifespan for startup/shutdown events (DB connection)
2. **Dependency injection**: Prepare for DI pattern with database sessions
3. **Type hints**: All functions fully typed for IDE support and validation
4. **Async endpoints**: Use async/await for I/O-bound operations

### Database Connection

1. **Connection pooling**: SQLModel handles pooling via SQLAlchemy engine
2. **Connection string format**: Use `postgresql+psycopg://` prefix for async driver
3. **SSL mode**: Enable SSL for Neon serverless connections (required)
4. **Graceful shutdown**: Close database connections on app shutdown

### Environment Configuration

1. **Required variable validation**: Fail fast on missing DATABASE_URL
2. **Sensitive value protection**: Never log or expose credential values
3. **Default values**: Only for non-sensitive, optional settings
4. **Type coercion**: Convert string env vars to appropriate types

## Dependencies Version Pinning

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | ^0.109.0 | Web framework |
| sqlmodel | ^0.0.14 | ORM with Pydantic integration |
| psycopg[binary] | ^3.1.0 | PostgreSQL driver |
| python-dotenv | ^1.0.0 | Environment variable loading |
| uvicorn[standard] | ^0.27.0 | ASGI server |
| pytest | ^8.0.0 | Testing framework |
| httpx | ^0.26.0 | Async HTTP client for testing |

## Open Questions (Resolved)

All technical questions resolved. No NEEDS CLARIFICATION items remaining.

## Next Steps

Proceed to Phase 1: Design & Contracts
- Generate data-model.md (minimal for setup phase)
- Create health endpoint contract in contracts/
- Write quickstart.md for developer onboarding
