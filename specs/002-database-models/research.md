# Research: Database Models

**Feature**: 002-database-models
**Date**: 2026-01-19
**Status**: Complete

## Technology Decisions

### 1. SQLModel for ORM

**Decision**: Use SQLModel as the ORM for defining database models.

**Rationale**:
- Already specified in constitution Technology Stack
- Native Pydantic integration for validation
- SQLAlchemy 2.0 foundation provides robust relationship support
- Type hints work seamlessly with FastAPI
- Single model definition serves both database and API schemas

**Alternatives Considered**:
- Pure SQLAlchemy - Rejected: requires separate Pydantic schemas for API
- Tortoise ORM - Rejected: async-only, not compatible with our sync database setup
- Django ORM - Rejected: too heavyweight, would require Django framework

### 2. UUID vs Integer Primary Keys

**Decision**: Use UUID primary keys for all entities.

**Rationale**:
- Globally unique across distributed systems
- No sequential guessing (security benefit)
- Works well with Neon's serverless architecture
- Standard practice for API-exposed resources
- Enables future horizontal scaling

**Alternatives Considered**:
- Auto-increment integers - Rejected: sequential IDs can be guessed, scaling issues
- ULID - Rejected: less standard library support in Python

### 3. Timestamp Implementation

**Decision**: Use `datetime` fields with `default_factory` for created_at and `sa_column` with `onupdate` for updated_at.

**Rationale**:
- SQLModel/SQLAlchemy handles UTC timezone automatically
- Server-side defaults ensure consistency even for direct DB access
- `onupdate` triggers work at database level for updated_at

**Alternatives Considered**:
- Application-level timestamps only - Rejected: inconsistent if DB accessed directly
- Database triggers - Rejected: adds complexity, less portable

### 4. Relationship Configuration

**Decision**: Use SQLModel's `Relationship` with `back_populates` for bidirectional relationships and `sa_relationship_kwargs` for cascade delete.

**Rationale**:
- Clear parent-child relationship definition
- Cascade delete handled at ORM level
- Easy navigation from Conversation to Messages and vice versa
- Consistent with SQLAlchemy patterns

**Alternatives Considered**:
- Database-level CASCADE - Considered: will add as backup, but ORM-level provides Python control
- Soft delete - Rejected: spec explicitly states hard delete

### 5. Migration Strategy

**Decision**: Use SQLModel's `SQLModel.metadata.create_all()` for initial schema creation.

**Rationale**:
- Simple and sufficient for development phase
- No additional tooling (Alembic) required initially
- Tables created atomically
- Can add Alembic later for schema evolution

**Alternatives Considered**:
- Alembic migrations - Deferred: overkill for initial setup, can add later
- Raw SQL scripts - Rejected: loses ORM benefits, more error-prone

### 6. Role Field for Messages

**Decision**: Use simple string field with validation, not a separate enum table.

**Rationale**:
- Only two values needed: "user", "assistant"
- Pydantic/SQLModel can validate at application level
- Simpler schema, fewer joins
- Easy to extend if needed later

**Alternatives Considered**:
- Enum column type - Considered: PostgreSQL ENUM requires migration for changes
- Separate roles table - Rejected: over-engineering for two static values

## Best Practices Applied

### SQLModel Models

1. **Table=True**: Mark classes that should create tables
2. **Optional fields**: Use `Optional[str]` with `default=None` for nullable
3. **Field constraints**: Use `Field()` for max_length, default values
4. **Relationships**: Define on both sides with `back_populates`

### Database Constraints

1. **Foreign keys**: Define with `Field(foreign_key="table.column")`
2. **Cascade delete**: Configure via `sa_relationship_kwargs={"cascade": "all, delete-orphan"}`
3. **NOT NULL**: Non-optional fields automatically NOT NULL
4. **Indexes**: Add indexes on frequently queried columns (user_id, conversation_id)

### Code Organization

1. **Separate model files**: One file per entity for maintainability
2. **Models package**: `__init__.py` exports all models
3. **Import order**: Base/shared types first, then entities by dependency order

## Open Questions (Resolved)

All technical questions resolved. No NEEDS CLARIFICATION items remaining.

## Next Steps

Proceed to Phase 1: Design & Contracts
- Generate detailed data-model.md with field definitions
- Create quickstart.md for model usage
- No API contracts needed (models-only feature)
