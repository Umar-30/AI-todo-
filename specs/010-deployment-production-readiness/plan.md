# Implementation Plan: Deployment & Production Readiness

**Branch**: `010-deployment-production-readiness` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-deployment-production-readiness/spec.md`

## Summary

Deploy the Cloud-Native Todo Chatbot (6 services + infrastructure) to both local Minikube and cloud managed Kubernetes (DOKS). Extend the existing Helm chart with Dapr-annotated microservice templates. Implement a GitHub Actions CI/CD pipeline that builds Docker images, pushes to GHCR, and deploys to Kubernetes. Enable structured logging, health checks, and basic broker visibility.

## Technical Context

**Language/Version**: Python 3.11 (backend + microservices), Node.js/Next.js (frontend)
**Primary Dependencies**: FastAPI, Dapr, Helm v3, Docker, GitHub Actions
**Storage**: Neon PostgreSQL (external), Redis (in-cluster), Redpanda/Redpanda Cloud
**Testing**: Smoke tests (kubectl-based health verification), Helm lint, dry-run
**Target Platform**: Kubernetes (Minikube local, DOKS cloud)
**Project Type**: Multi-service web application (monorepo)
**Performance Goals**: All services healthy within 2 min of pod creation, CI/CD completes in <15 min
**Constraints**: No direct Kafka clients, all messaging via Dapr HTTP APIs, no hard-coded secrets
**Scale/Scope**: 6 services, 3 Kafka topics, 4 Dapr components, 2 environments

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. MCP-Compliant Architecture | PASS | No application logic changes |
| II. Database as Single Source of Truth | PASS | No data layer changes |
| III. Stateless Agent Design | PASS | No agent changes |
| IV. Tool-Driven Operations | PASS | No tool changes |
| V. AI Behavior Constraints | PASS | No AI changes |
| VI. Security and Authentication | PASS | Secrets externalized, no hard-coding |
| VII. Non-Implementation Principle | PASS | Infrastructure-only changes |
| VIII. AI-First Tooling | PASS | Using Helm, Docker, Dapr CLI |
| IX. Local-Only Deployment | **VIOLATION** | Phase V explicitly requires cloud deployment |
| X. Spec-Driven Infrastructure | PASS | All infra defined in specs/contracts |
| XI. Beginner-Friendly Simplicity | PASS | Standard Helm + GitHub Actions patterns |
| XII. Structured Output | PASS | All artifacts declarative and reproducible |
| XIII. AIOps Alignment | PASS | Observability, automation prioritized |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Principle IX: Cloud deployment | Phase V user requirement explicitly requests cloud K8s deployment (DOKS/GKE/AKS). Principle IX was scoped to Phase IV. | Local-only cannot ship the product to real users. |

## Project Structure

### Documentation (this feature)

```text
specs/010-deployment-production-readiness/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Research findings
├── data-model.md        # Configuration entities
├── quickstart.md        # Deployment quickstart guide
├── contracts/
│   ├── helm-values-schema.yaml
│   ├── cicd-workflow-contract.yaml
│   └── service-inventory.yaml
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
# Backend + Microservices
backend/
├── Dockerfile               # TO CREATE
├── src/
│   ├── api/
│   ├── events/
│   ├── models/
│   ├── mcp/
│   └── services/

services/
├── recurring-task-service/
│   ├── Dockerfile           # EXISTS
│   └── src/
├── realtime-sync-service/
│   ├── Dockerfile           # EXISTS
│   └── src/
├── reminder-service/
│   ├── Dockerfile           # TO CREATE
│   └── src/
└── audit-service/
    ├── Dockerfile           # TO CREATE
    └── src/

# Frontend
AI-todo-new/
├── Dockerfile               # EXISTS
└── ...

# Infrastructure
k8s/
├── helm/todo-chatbot/
│   ├── Chart.yaml           # UPDATE (version bump)
│   ├── values.yaml          # UPDATE (add microservices + dapr)
│   ├── values-local.yaml    # TO CREATE
│   ├── values-cloud.yaml    # TO CREATE
│   └── templates/
│       ├── backend-deployment.yaml      # UPDATE (add Dapr annotations)
│       ├── recurring-task-deployment.yaml # TO CREATE
│       ├── realtime-sync-deployment.yaml  # TO CREATE
│       ├── reminder-deployment.yaml       # TO CREATE
│       ├── audit-deployment.yaml          # TO CREATE
│       ├── dapr-components.yaml           # TO CREATE
│       └── _helpers.tpl                   # UPDATE (add new helpers)
├── manifests/
│   ├── redpanda/
│   └── redis/

dapr/
└── components/
    ├── pubsub-redpanda.yaml     # EXISTS
    ├── statestore-redis.yaml    # EXISTS
    ├── secrets-local.yaml       # EXISTS
    └── cron-reminder.yaml       # EXISTS

# CI/CD
.github/
└── workflows/
    └── deploy.yml               # TO CREATE
```

**Structure Decision**: Extend existing Helm chart in `k8s/helm/todo-chatbot/` with new templates for the 4 microservices and Dapr components. Use values overlay files for environment separation.

---

## Implementation Stages

### Stage 1: Dockerfiles (Day 1)

**Goal**: Every service has a working Dockerfile.

| Task | Description |
|------|-------------|
| Create `backend/Dockerfile` | Python 3.11 slim, install deps, copy src, expose 8000 |
| Create `services/reminder-service/Dockerfile` | Python 3.11 slim, port 8003 |
| Create `services/audit-service/Dockerfile` | Python 3.11 slim, port 8004 |
| Verify existing Dockerfiles | Confirm recurring-task and realtime-sync Dockerfiles work |
| Verify frontend Dockerfile | Confirm AI-todo-new/Dockerfile builds correctly |

**Validation**: All 6 images build with `docker build` without errors.

---

### Stage 2: Helm Chart Extension (Day 2-3)

**Goal**: Single Helm chart deploys all 6 services with Dapr annotations.

| Task | Description |
|------|-------------|
| Update `values.yaml` | Add recurringTask, realtimeSync, reminder, audit, dapr, redpanda, redis sections |
| Update `_helpers.tpl` | Add label/selector helpers for each microservice |
| Update `backend-deployment.yaml` | Add Dapr sidecar annotations |
| Create `recurring-task-deployment.yaml` | Templated deployment + service |
| Create `realtime-sync-deployment.yaml` | Templated deployment + service |
| Create `reminder-deployment.yaml` | Templated deployment + service |
| Create `audit-deployment.yaml` | Templated deployment + service |
| Create `dapr-components.yaml` | Templated Dapr PubSub and StateStore from values |
| Create `infrastructure.yaml` | Conditional Redpanda + Redis deployments (local only) |
| Run `helm lint` | Validate chart syntax |
| Run `helm template` with dry-run | Verify rendered manifests |

**Validation**: `helm lint` passes, `helm template` renders all 6 deployments correctly.

---

### Stage 3: Environment Values Files (Day 3)

**Goal**: Local and cloud environments differ only in values, not templates.

| Task | Description |
|------|-------------|
| Create `values-local.yaml` | Local broker URLs, IfNotPresent pullPolicy, 1 replica each |
| Create `values-cloud.yaml` | GHCR image repos, Redpanda Cloud URLs, 2 replicas, SASL auth |
| Validate environment separation | `helm template` with each values file shows correct config |

**Validation**: Diff between local and cloud rendered templates shows only expected differences (URLs, replicas, auth).

---

### Stage 4: Local Minikube Deployment (Day 4-5)

**Goal**: Full system running on Minikube with Dapr.

| Task | Description |
|------|-------------|
| Start Minikube with adequate resources | 4 CPUs, 8GB RAM |
| Install Dapr on K8s | `dapr init -k --wait` |
| Build all images on Minikube Docker | `eval $(minikube docker-env)` + build |
| Deploy with Helm (local values) | `helm upgrade --install` with values-local.yaml |
| Verify all pods running | `kubectl get pods` shows all Running |
| Verify Dapr sidecars | Each pod has 2/2 containers ready |
| Verify Dapr dashboard | All components healthy |
| Run smoke test | Create task, complete recurring task, check audit |

**Validation**: All 6 services healthy, Dapr dashboard shows components, end-to-end task flow works.

---

### Stage 5: CI/CD Pipeline (Day 6-7)

**Goal**: Automated build/push/deploy via GitHub Actions.

| Task | Description |
|------|-------------|
| Create `.github/workflows/deploy.yml` | Main workflow file |
| Implement change detection job | dorny/paths-filter or git diff for service paths |
| Implement build job | Matrix strategy, docker build per changed service |
| Implement push job | Login to GHCR, push with SHA + latest tags |
| Implement deploy job | Setup kubeconfig, helm upgrade with values-cloud.yaml |
| Add secret creation step | kubectl create/update secrets from GitHub Actions secrets |
| Add rollout verification | kubectl rollout status with timeout |
| Add failure handling | Fail-fast on build, rollback on deploy failure |
| Test pipeline (dry run) | Push to feature branch, verify build-only (no deploy) |

**Validation**: Push to main triggers pipeline, all stages complete, services updated on cluster.

---

### Stage 6: Cloud Deployment (Day 8-9)

**Goal**: System running on managed K8s with Redpanda Cloud.

| Task | Description |
|------|-------------|
| Create/configure cloud K8s cluster | DOKS with doctl or equivalent |
| Install Dapr on cloud cluster | `dapr init -k --wait` |
| Provision Redpanda Cloud topic | Create task-events, reminders, task-updates |
| Create Kubernetes secrets | Database, JWT, API keys, Redpanda SASL |
| Update values-cloud.yaml | Real Redpanda Cloud URLs and GHCR image paths |
| Deploy with Helm (cloud values) | `helm upgrade --install` with values-cloud.yaml |
| Verify all pods running | Health checks pass for all services |
| Run smoke test | End-to-end task flow via browser |

**Validation**: All services healthy on cloud K8s, frontend accessible, events flowing through Redpanda Cloud.

---

### Stage 7: Monitoring & Logging (Day 9-10)

**Goal**: Structured logs, health visibility, broker monitoring.

| Task | Description |
|------|-------------|
| Configure JSON log format | Update Python logging config to JSON formatter |
| Verify correlation IDs in logs | Trace a request across backend → Dapr → microservice |
| Verify health endpoints | All 6 services respond 200 on /health |
| Configure Redpanda Console | Access Redpanda Cloud console for topic/consumer visibility |
| Document monitoring procedures | How to check logs, health, consumer lag |

**Validation**: `kubectl logs` shows JSON, correlation IDs match across services, consumer lag visible.

---

### Stage 8: Validation & Polish (Day 10-11)

**Goal**: Environment parity verified, documentation complete.

| Task | Description |
|------|-------------|
| Compare local vs cloud deployments | Verify only values differ, not structure |
| Test CI/CD end-to-end | Push change → auto-deploy → verify |
| Update Helm chart version | Bump Chart.yaml version |
| Validate quickstart.md | Follow quickstart steps on clean machine |
| Document rollback procedure | helm rollback command and verification |

**Validation**: All success criteria from spec met.

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Minikube resource exhaustion (6 services + infra) | High | Set minimum 4 CPU / 8GB RAM, use resource limits |
| Redpanda Cloud auth misconfiguration | Medium | Test SASL locally with Redpanda's auth before cloud |
| GHCR rate limiting | Low | Use GITHUB_TOKEN (built-in), higher limits |
| Dapr sidecar injection failures | Medium | Verify namespace annotations, check Dapr logs |
| Helm template rendering bugs | Medium | Iterative `helm template` + `kubeval` validation |

---

## Dependencies

```
Stage 1 (Dockerfiles)
  └── Stage 2 (Helm Chart) ─── Stage 3 (Values Files)
        │                          │
        └── Stage 4 (Local Deploy) ┘
              │
              ├── Stage 5 (CI/CD) ── Stage 6 (Cloud Deploy)
              │                            │
              └── Stage 7 (Monitoring) ────┘
                                           │
                                    Stage 8 (Validation)
```

## Timeline Estimate

| Stage | Duration | Cumulative |
|-------|----------|-----------|
| 1. Dockerfiles | 1 day | Day 1 |
| 2. Helm Chart Extension | 2 days | Day 3 |
| 3. Environment Values | 0.5 day | Day 3.5 |
| 4. Local Minikube | 1.5 days | Day 5 |
| 5. CI/CD Pipeline | 2 days | Day 7 |
| 6. Cloud Deployment | 1.5 days | Day 8.5 |
| 7. Monitoring | 1 day | Day 9.5 |
| 8. Validation | 1.5 days | Day 11 |
| **Total** | **~11 days** | |
