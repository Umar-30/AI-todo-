<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version change: 1.0.0 → 2.0.0 (MAJOR: Phase IV Local Kubernetes Deployment)

Modified principles:
- None modified (all Phase III principles retained)

Added sections:
- Phase IV Scope Declaration
- 7 new Phase IV Principles (VII-XIII)
- Phase IV Tooling Stack
- Phase IV Deployment Workflow

Removed sections: None

Templates requiring updates:
- .specify/templates/plan-template.md: ✅ Compatible (supports infrastructure planning)
- .specify/templates/spec-template.md: ✅ Compatible (requirements section supports K8s specs)
- .specify/templates/tasks-template.md: ✅ Compatible (phase structure supports K8s tasks)

Follow-up TODOs: None
================================================================================
-->

# Todo AI Chatbot Constitution

## Phase IV Scope Declaration

This constitution defines rules for **Phase IV: Local Kubernetes Deployment**.

**In Scope**:
- Architecture, workflow, and tooling for local Kubernetes deployment
- Spec-driven infrastructure definitions
- AI-assisted generation of Docker, Helm, and Kubernetes resources

**Out of Scope**:
- Modification of Phase III application logic
- Production code implementation
- Cloud provider deployments

---

## Core Principles (Phase III - Application)

### I. MCP-Compliant Architecture

All task operations MUST be executed through MCP (Model Context Protocol) tools.
The system MUST maintain a clear separation between AI logic, tools, and APIs.
Tools MUST validate input and persist state to the database.
Tools MUST return deterministic, typed outputs.
No in-memory or internal tool state is allowed.

**Rationale**: MCP compliance ensures reproducibility, auditability, and clean boundaries
between components. Stateless tools enable horizontal scaling and simplify debugging.

### II. Database as Single Source of Truth

All application state MUST be persisted to the database (Neon Serverless PostgreSQL).
Conversation state MUST be stored in the database, not in memory.
Agents and tools MUST NOT maintain internal state between invocations.
All data access MUST go through SQLModel ORM.

**Rationale**: A single source of truth eliminates state synchronization issues,
enables stateless deployment, and provides clear audit trails for all operations.

### III. Stateless Agent Design

AI agents MUST be stateless between requests.
The chat endpoint MUST be stateless with conversation state persisted to DB.
Agents MUST NOT access the database directly; all data operations MUST use MCP tools.
Each request MUST be self-contained with all required context.

**Rationale**: Stateless agents enable horizontal scaling, simplify testing,
and ensure reproducible behavior across invocations.

### IV. Tool-Driven Operations

All task operations MUST use MCP tools exclusively.
The AI layer MUST translate user intent into MCP tool calls.
The `add_task` tool MUST accept: user_id (string, required), title (string, required),
description (string, optional) and return: task_id, status, title.
Tools MUST validate all input before executing operations.

**Rationale**: Tool-driven architecture creates explicit, testable contracts
between components and ensures all operations are auditable.

### V. AI Behavior Constraints

The AI MUST translate user intent into appropriate MCP tool calls.
The AI MUST ask clarifying questions when intent is ambiguous.
The AI MUST confirm tool execution before responding to the user.
The AI MUST NOT access the database directly.
The AI MUST NOT include sensitive data in responses.

**Rationale**: Clear AI behavior constraints ensure predictable interactions,
protect user data, and maintain system integrity.

### VI. Security and Authentication

Authentication MUST be required for all operations (via Better Auth).
User context MUST be provided for all task actions.
No sensitive data MUST appear in AI responses.
All API endpoints MUST validate authentication before processing.

**Rationale**: Security is non-negotiable. Authentication ensures user isolation
and protects against unauthorized access to task data.

---

## Core Principles (Phase IV - Kubernetes Deployment)

### VII. Non-Implementation Principle

Phase IV MUST NOT modify Phase III application logic.
Focus MUST be solely on architecture, workflow, and tooling for deployment.
All specifications MUST be infrastructure-focused, not application-focused.

**Rationale**: Clear separation between application development (Phase III) and
deployment infrastructure (Phase IV) prevents scope creep and maintains clean boundaries.

### VIII. AI-First Tooling

Docker tasks MUST prefer **Docker AI (Gordon)** when available.
Kubernetes tasks MUST prefer **kubectl-ai** and **Kagent** when available.
Standard CLI tools MAY be used only when AI tools are unavailable.

**Rationale**: AI-assisted tooling accelerates development, reduces human error,
and aligns with AIOps best practices for cloud-native deployments.

### IX. Local-Only Deployment

All deployments MUST target **Minikube** for local Kubernetes.
No cloud provider resources (AWS, GCP, Azure) are allowed.
External dependencies MUST be mocked or containerized locally.

**Rationale**: Local-only deployment ensures reproducibility, eliminates cloud costs,
and provides a safe environment for learning and experimentation.

### X. Spec-Driven Infrastructure

Infrastructure MUST be defined as specifications or blueprints first.
AI-assisted generation MUST be used for Docker, Helm, and Kubernetes resources.
All generated resources MUST be validated against specifications.

**Rationale**: Spec-driven infrastructure ensures consistency, enables version control,
and provides clear documentation for all deployment artifacts.

### XI. Beginner-Friendly Simplicity

Specifications MUST be written for beginners to understand.
Avoid unnecessary complexity in architecture and tooling.
Prefer simple, well-documented approaches over advanced techniques.

**Rationale**: Simplicity reduces the learning curve, minimizes errors,
and ensures the project remains accessible to new contributors.

### XII. Structured Output

All output MUST be structured and reproducible.
Deployment artifacts MUST follow cloud-native best practices.
Documentation MUST accompany all infrastructure definitions.

**Rationale**: Structured, reproducible output enables automation,
facilitates troubleshooting, and supports continuous improvement.

### XIII. AIOps Alignment

Deployment workflows MUST align with AIOps best practices.
Observability MUST be considered in all infrastructure specifications.
Automation MUST be preferred over manual intervention.

**Rationale**: AIOps alignment ensures the deployment infrastructure is
modern, maintainable, and ready for production-grade operations.

---

## Technology Stack

### Application (Phase III)

**Frontend**: OpenAI ChatKit
**Backend**: FastAPI (Python)
**AI Framework**: OpenAI Agents SDK
**MCP Server**: Official MCP SDK
**ORM**: SQLModel
**Database**: Neon Serverless PostgreSQL
**Auth**: Better Auth

### Deployment (Phase IV)

**Container Runtime**: Docker
**Container Orchestration**: Kubernetes (Minikube)
**Package Management**: Helm
**AI Tooling**: Docker AI (Gordon), kubectl-ai, Kagent
**Infrastructure as Code**: Kubernetes manifests, Helm charts

All technology choices are mandatory. Deviations require explicit justification
and constitution amendment.

---

## Development Workflow

### Conversational Task Management (Phase III)

Users interact with the system through natural language chat.
The AI interprets user intent and executes appropriate MCP tool calls.
All task CRUD operations flow through the MCP server.
The system confirms successful operations before responding.

### Infrastructure Development (Phase IV)

1. Define infrastructure requirements as specifications
2. Use AI tools to generate Docker, Helm, and Kubernetes resources
3. Validate generated resources against specifications
4. Deploy to local Minikube cluster
5. Verify deployment and document results

### Testing Requirements

All MCP tools MUST have contract tests verifying input/output types.
Integration tests MUST verify end-to-end chat-to-database flows.
All tools MUST be tested for deterministic, reproducible outputs.
Kubernetes manifests MUST be validated with `kubectl --dry-run`.
Helm charts MUST pass `helm lint` validation.

### Deployment Requirements (Phase III)

The system MUST be stateless and reproducible.
All state MUST be externalized to the database.
The chat endpoint MUST handle concurrent requests without state conflicts.

### Deployment Requirements (Phase IV)

Minikube MUST be the sole deployment target.
All services MUST be containerized with Docker.
Kubernetes resources MUST be defined declaratively.
Secrets MUST use Kubernetes Secrets, not hardcoded values.

---

## Governance

This constitution supersedes all other development practices and guidelines.
All code changes MUST verify compliance with these principles.

**Amendment Process**:
1. Document proposed changes with rationale
2. Assess impact on existing system components
3. Update all dependent templates and documentation
4. Increment version according to semantic versioning:
   - MAJOR: Breaking changes to principles or architecture
   - MINOR: New principles or expanded guidance
   - PATCH: Clarifications or typo fixes

**Compliance Review**:
All pull requests MUST include a constitution compliance check.
Violations MUST be justified with explicit tradeoff documentation.

**Version**: 2.0.0 | **Ratified**: 2026-01-19 | **Last Amended**: 2026-02-03
