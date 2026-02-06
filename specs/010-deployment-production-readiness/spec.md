# Feature Specification: Deployment & Production Readiness

**Feature Branch**: `010-deployment-production-readiness`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Phase V: Deployment and Production Readiness for the Cloud-Native Todo Chatbot system"

## System Context

The Cloud-Native Todo Chatbot is a multi-service system consisting of:

- **Frontend**: Next.js web application
- **Backend**: FastAPI application with MCP tools, SSE events, and Dapr integration
- **Recurring Task Service**: FastAPI microservice for auto-generating recurring task instances
- **Realtime Sync Service**: FastAPI + WebSocket service for live task synchronization
- **Reminder Service**: FastAPI microservice for due date reminder scheduling
- **Audit Service**: FastAPI microservice for immutable task change logging
- **Infrastructure**: Redpanda (Kafka-compatible broker), Redis (Dapr state store), PostgreSQL (Neon)
- **Runtime**: Dapr sidecars on all services for Pub/Sub, state management, and service invocation

This specification defines how the entire system moves from local development to a production-grade deployment.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Local Deployment on Minikube (Priority: P1)

As a developer, I need to deploy the complete Todo Chatbot system on my local Minikube cluster with all services, Dapr sidecars, Redpanda, and Redis running, so that I can develop, test, and demonstrate the full system locally.

**Why this priority**: Without a working local deployment, no developer can test, debug, or iterate on the system. This is the foundation for all other stories.

**Independent Test**: Start Minikube, run the deployment, open the frontend in a browser, create a task with recurrence, and verify the recurring task service creates the next occurrence via Dapr Pub/Sub.

**Acceptance Scenarios**:

1. **Given** a clean Minikube cluster with Dapr installed, **When** the developer runs the local deployment procedure, **Then** all 6 services (frontend, backend, recurring-task, realtime-sync, reminder, audit) start with healthy Dapr sidecars and the frontend is accessible via browser.
2. **Given** all services are running locally, **When** a user creates a recurring task and marks it complete, **Then** the recurring task service auto-creates the next occurrence within 5 seconds.
3. **Given** the local deployment is running, **When** a service pod is restarted, **Then** it recovers and reconnects to Dapr Pub/Sub within 30 seconds without data loss.
4. **Given** the local deployment, **When** the developer checks Dapr dashboard, **Then** all components (pubsub-redpanda, statestore-redis) show as healthy.

---

### User Story 2 - Cloud Deployment to Managed Kubernetes (Priority: P1)

As a DevOps engineer, I need to deploy the system to a managed Kubernetes cluster (DigitalOcean DOKS, Google GKE, or Azure AKS) with Redpanda Cloud for messaging and externalized secrets, so that the application is accessible to end users in a production environment.

**Why this priority**: The system must run in the cloud for real users. Without cloud deployment, the product cannot be shipped.

**Independent Test**: Deploy to a managed K8s cluster, access the frontend via a public URL, and verify all services communicate correctly through Dapr and Redpanda Cloud.

**Acceptance Scenarios**:

1. **Given** a managed Kubernetes cluster with Dapr enabled, **When** the cloud deployment procedure is executed, **Then** all services deploy successfully with Dapr sidecars and connect to Redpanda Cloud.
2. **Given** the cloud deployment, **When** the Redpanda Cloud broker URL is changed, **Then** only the Dapr Pub/Sub component configuration needs updating (no service code changes).
3. **Given** the cloud environment, **When** a developer inspects environment variables, **Then** no secrets (database URLs, API keys, broker credentials) are hard-coded in any manifest or image.
4. **Given** the cloud deployment, **When** a user accesses the frontend, **Then** the system responds within normal performance expectations for a web application.

---

### User Story 3 - Automated CI/CD Pipeline (Priority: P2)

As a developer, I need an automated pipeline that builds Docker images, pushes them to a container registry, and deploys updates to Kubernetes on every push to the main branch, so that deployments are consistent, repeatable, and require no manual steps.

**Why this priority**: Automated deployments reduce human error and speed up the development cycle. Important but the system can initially be deployed manually.

**Independent Test**: Push a code change to the main branch, verify the pipeline triggers, builds images, pushes to registry, and updates the Kubernetes deployment.

**Acceptance Scenarios**:

1. **Given** a code push to the main branch, **When** the CI/CD pipeline triggers, **Then** Docker images for all changed services are built and tagged with the commit SHA.
2. **Given** built images, **When** the pipeline pushes to the container registry, **Then** images are available with both `latest` and commit-specific tags.
3. **Given** pushed images, **When** the pipeline deploys to Kubernetes, **Then** the rolling update completes without downtime and all health checks pass.
4. **Given** a pipeline failure during image build, **When** the developer reviews the pipeline, **Then** the failure reason is clearly reported and no partial deployment occurs.

---

### User Story 4 - Monitoring and Observability (Priority: P2)

As an operator, I need to view application logs, check service health, and monitor message broker activity, so that I can detect and diagnose issues in the running system.

**Why this priority**: Observability is essential for maintaining a production system, but the system can launch with basic monitoring and expand over time.

**Independent Test**: Deploy the system, trigger a task creation, and verify the event flow is visible through logs and health endpoints across all services.

**Acceptance Scenarios**:

1. **Given** a running deployment, **When** an operator queries application logs, **Then** structured logs from all services are accessible in a centralized location with timestamps and service identifiers.
2. **Given** a running deployment, **When** an operator checks health endpoints, **Then** every service exposes a health endpoint that reports service status and dependency connectivity (Dapr, database, broker).
3. **Given** a running deployment, **When** an operator inspects the message broker, **Then** basic Kafka consumer group status (lag, offsets, active consumers) is visible.
4. **Given** a service experiencing errors, **When** the operator reviews logs, **Then** error context (correlation IDs, request traces, event types) is present to diagnose the issue.

---

### User Story 5 - Environment Parity (Priority: P3)

As a developer, I need the local Minikube deployment to closely mirror the cloud deployment, so that issues caught locally are representative of production behavior and vice versa.

**Why this priority**: Environment parity reduces "works on my machine" issues but is a quality concern, not a launch blocker.

**Independent Test**: Compare the local and cloud Dapr component configurations, Kubernetes manifests, and service deployment patterns to verify structural equivalence.

**Acceptance Scenarios**:

1. **Given** local and cloud Helm values files, **When** a developer compares them, **Then** only environment-specific values differ (broker URLs, resource limits, replica counts) and not structural configuration.
2. **Given** both environments, **When** a developer reviews Dapr component definitions, **Then** the same component types (pubsub.kafka, state.redis) are used with only connection parameters differing.
3. **Given** the local environment, **When** a new microservice is added, **Then** the same Helm template and Dapr annotation pattern used in cloud applies locally with only values overrides.

---

### Edge Cases

- What happens when the Dapr sidecar fails to start alongside a service pod?
- What happens when Redpanda is temporarily unavailable during deployment?
- What happens when a CI/CD pipeline runs concurrently on multiple branches?
- How does the system handle a cloud provider API outage during deployment?
- What happens when the container registry rate-limits image pushes?
- What happens when a Kubernetes cluster runs out of resources during scaling?
- What happens when database migrations fail during a rolling update?

## Architecture Overview

```
Local (Minikube)                          Cloud (DOKS/GKE/AKS)
┌──────────────────────┐                 ┌──────────────────────┐
│  Minikube Cluster     │                │  Managed K8s Cluster  │
│                       │                │                       │
│  ┌──────┐ ┌────────┐ │                │  ┌──────┐ ┌────────┐ │
│  │Front │ │Backend │ │                │  │Front │ │Backend │ │
│  │ end  │ │+Dapr   │ │                │  │ end  │ │+Dapr   │ │
│  └──────┘ └────────┘ │                │  └──────┘ └────────┘ │
│  ┌────────┐┌───────┐ │                │  ┌────────┐┌───────┐ │
│  │Recur.  ││Remind.│ │                │  │Recur.  ││Remind.│ │
│  │+Dapr   ││+Dapr  │ │                │  │+Dapr   ││+Dapr  │ │
│  └────────┘└───────┘ │                │  └────────┘└───────┘ │
│  ┌────────┐┌───────┐ │                │  ┌────────┐┌───────┐ │
│  │Realtime││Audit  │ │                │  │Realtime││Audit  │ │
│  │+Dapr   ││+Dapr  │ │                │  │+Dapr   ││+Dapr  │ │
│  └────────┘└───────┘ │                │  └────────┘└───────┘ │
│                       │                │                       │
│  ┌─────────┐┌──────┐ │                │  Redpanda Cloud       │
│  │Redpanda ││Redis │ │                │  (Serverless)         │
│  │(Docker) ││      │ │                │  ┌──────┐             │
│  └─────────┘└──────┘ │                │  │Redis │ (managed)   │
│  Dapr Components      │                │  └──────┘             │
└──────────────────────┘                │  Dapr Components      │
                                         └──────────────────────┘

                    GitHub Actions CI/CD
                    ┌──────────────────┐
                    │ Build → Push →   │
                    │ Deploy (auto)    │
                    └──────────────────┘
```

## Requirements *(mandatory)*

### Functional Requirements

#### Local Deployment (Minikube)

- **FR-001**: System MUST deploy all services (frontend, backend, recurring-task-service, realtime-sync-service, reminder-service, audit-service) on a single Minikube cluster.
- **FR-002**: System MUST install and configure Dapr runtime on the Minikube cluster with all required components (pubsub-redpanda, statestore-redis, secrets-local, cron-reminder).
- **FR-003**: System MUST deploy Redpanda as a single-node container within the Minikube cluster for Kafka-compatible messaging.
- **FR-004**: System MUST deploy Redis within the Minikube cluster for Dapr state storage.
- **FR-005**: System MUST ensure every application service runs with a Dapr sidecar injected automatically via Kubernetes annotations.
- **FR-006**: System MUST provide a Helm chart (or extend the existing one) that deploys the complete local stack with a single command.
- **FR-007**: System MUST create Kafka topics (task-events, reminders, task-updates) during local deployment setup.

#### Cloud Deployment

- **FR-008**: System MUST deploy to at least one managed Kubernetes platform (DOKS, GKE, or AKS) with Dapr enabled.
- **FR-009**: System MUST use Redpanda Cloud (Serverless) as the Kafka-compatible message broker in cloud environments.
- **FR-010**: System MUST externalize all secrets (database URLs, API keys, broker credentials) using Kubernetes secrets or a secrets management solution.
- **FR-011**: System MUST NOT contain any hard-coded secrets, connection strings, or environment-specific values in Docker images or source code.
- **FR-012**: System MUST provide environment-specific Helm values files (values-local.yaml, values-cloud.yaml) that override only connection parameters.
- **FR-013**: System MUST support configuring the Redpanda Cloud broker endpoint via Dapr component metadata without changing service code.

#### CI/CD Pipeline

- **FR-014**: System MUST provide a GitHub Actions workflow that triggers on pushes to the main branch.
- **FR-015**: The pipeline MUST build Docker images for all services that have changed in the commit.
- **FR-016**: The pipeline MUST push built images to a container registry with both a commit SHA tag and a `latest` tag.
- **FR-017**: The pipeline MUST deploy updated services to the target Kubernetes cluster after successful image push.
- **FR-018**: The pipeline MUST manage secrets through GitHub Actions secrets (never in workflow files or source code).
- **FR-019**: The pipeline MUST fail fast and prevent partial deployments if any build step fails.
- **FR-020**: System MUST provide Dockerfiles for all services that currently lack them (backend, frontend, reminder-service, audit-service).

#### Monitoring & Observability

- **FR-021**: All services MUST emit structured JSON logs with timestamps, log levels, service names, and correlation IDs.
- **FR-022**: All services MUST expose a `/health` endpoint that reports the service's operational status and dependency connectivity.
- **FR-023**: System MUST provide visibility into Kafka consumer group status (consumer lag, active consumers) through Redpanda's built-in tools or Dapr dashboard.
- **FR-024**: System MUST preserve correlation IDs across service boundaries (from initial API request through Pub/Sub events to downstream services).

### Key Entities

- **Deployment Environment**: Represents a target deployment (local or cloud), including cluster configuration, Helm values, and secrets.
- **Service Image**: A Docker image for a specific service, tagged with commit SHA and `latest`, stored in a container registry.
- **Pipeline Run**: A CI/CD execution triggered by a code push, containing build, push, and deploy stages with pass/fail status.
- **Dapr Component Configuration**: Environment-specific Dapr component definitions that vary only in connection parameters between local and cloud.
- **Health Status**: Per-service operational status including dependency connectivity (Dapr, database, broker).

## Assumptions

- The managed Kubernetes cluster is pre-provisioned (cluster creation is not part of this specification).
- Redpanda Cloud Serverless account is pre-provisioned with appropriate billing.
- PostgreSQL database (Neon) is already provisioned and accessible from both local and cloud environments.
- Container registry (Docker Hub, GHCR, or DigitalOcean Container Registry) is pre-provisioned.
- Developers have `kubectl`, `helm`, `dapr`, and `docker` CLI tools installed locally.
- The existing Helm chart at `k8s/helm/todo-chatbot/` will be extended (not replaced) for new services.

## Constraints

- Reuse Phase IV Helm charts and manifests where possible; extend rather than replace.
- All messaging MUST go through Dapr HTTP APIs (no direct Kafka client libraries in any service).
- Local and cloud environments MUST use the same Dapr component types with only connection-parameter differences.
- CI/CD pipeline uses GitHub Actions only (no other CI providers).
- Focus on operational essentials; advanced features (auto-scaling, blue/green deployments, distributed tracing dashboards) are out of scope.

## Out of Scope

- Auto-scaling policies (HPA configuration)
- Blue/green or canary deployment strategies
- Distributed tracing UI (Jaeger/Zipkin integration)
- Performance load testing infrastructure
- Multi-region or multi-cluster deployment
- Custom domain and TLS/SSL certificate provisioning
- Database backup and disaster recovery procedures

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can deploy the complete system on Minikube and have all services healthy within 10 minutes of running the deployment command.
- **SC-002**: All 6 services start with Dapr sidecars and report healthy via their `/health` endpoints within 2 minutes of pod creation.
- **SC-003**: The cloud deployment runs on a managed Kubernetes cluster with Redpanda Cloud, with zero hard-coded secrets in images or manifests.
- **SC-004**: A code push to main triggers the CI/CD pipeline, and updated services are live on the cluster within 15 minutes.
- **SC-005**: An operator can view structured logs from any service and trace a request across services using correlation IDs.
- **SC-006**: Switching between local and cloud environments requires changing only the Helm values file (no code or Dapr component type changes).
- **SC-007**: The CI/CD pipeline detects a build failure and stops before any deployment occurs, with a clear error message.
- **SC-008**: Consumer lag for all Kafka topics is visible through Redpanda tooling or Dapr dashboard.
