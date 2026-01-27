# Data Model: Project Setup

**Feature**: 001-project-setup
**Date**: 2026-01-19
**Status**: Complete

## Overview

This phase establishes database connectivity only. No domain entities (tasks, users, conversations) are defined in this phase per the spec scope boundaries.

## Entities

### HealthStatus (Response Model Only)

A response-only model for the health check endpoint. Not persisted to database.

| Field | Type | Description |
|-------|------|-------------|
| status | string | Overall system status ("healthy", "unhealthy") |
| server | string | Server status ("running") |
| database | string | Database connection status ("connected", "disconnected") |
| timestamp | datetime | ISO 8601 timestamp of health check |

**Validation Rules**:
- status: Enum of "healthy" or "unhealthy"
- timestamp: UTC timezone, ISO 8601 format

**State Transitions**: None (read-only response model)

## Database Schema

No tables created in this phase. Database connection is verified only.

Future phases will add:
- Users table (authentication feature)
- Tasks table (todo management feature)
- Conversations table (chat history feature)

## Configuration Entities

### Environment Configuration

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| DATABASE_URL | string | Yes | Neon PostgreSQL connection string |
| OPENAI_API_KEY | string | Yes | OpenAI API key for future AI features |

**Validation Rules**:
- DATABASE_URL: Must start with `postgresql://` or `postgres://`
- OPENAI_API_KEY: Must be non-empty string (not validated in this phase)

## Relationships

No entity relationships in this phase. Health status is a standalone response model.

## Notes

- This is an infrastructure-only phase
- Domain models (Task, User, Conversation) will be defined in subsequent features
- The data model will grow as features are added per the constitution's MCP-compliant architecture
