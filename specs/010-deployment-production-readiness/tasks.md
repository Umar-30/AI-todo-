# Tasks: Deployment & Production Readiness

**Input**: Design documents from `/specs/010-deployment-production-readiness/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Helm Chart**: `k8s/helm/todo-chatbot/`
- **Templates**: `k8s/helm/todo-chatbot/templates/`
- **Dockerfiles**: `backend/`, `services/{service-name}/`
- **CI/CD**: `.github/workflows/`
- **Dapr**: `dapr/components/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dockerfiles and Helm chart foundation for all environments

### Dockerfiles

- [ ] T001 [P] Create backend Dockerfile in backend/Dockerfile (Python 3.11-slim, install deps, copy src, expose 8000)
- [ ] T002 [P] Create reminder-service Dockerfile in services/reminder-service/Dockerfile (Python 3.11-slim, port 8003)
- [ ] T003 [P] Create audit-service Dockerfile in services/audit-service/Dockerfile (Python 3.11-slim, port 8004)
- [ ] T004 [P] Verify existing recurring-task-service Dockerfile builds successfully in services/recurring-task-service/Dockerfile
- [ ] T005 [P] Verify existing realtime-sync-service Dockerfile builds successfully in services/realtime-sync-service/Dockerfile
- [ ] T006 Verify existing frontend Dockerfile builds successfully in AI-todo-new/Dockerfile

### Helm Chart Extension

- [ ] T007 Update values.yaml with microservice sections (recurringTask, realtimeSync, reminder, audit) in k8s/helm/todo-chatbot/values.yaml
- [ ] T008 Add Dapr and infrastructure sections (dapr, redpanda, redis) to values.yaml in k8s/helm/todo-chatbot/values.yaml
- [ ] T009 Update _helpers.tpl with label/selector helpers for each microservice in k8s/helm/todo-chatbot/templates/_helpers.tpl
- [ ] T010 Update backend-deployment.yaml to add Dapr sidecar annotations in k8s/helm/todo-chatbot/templates/backend-deployment.yaml
- [ ] T011 [P] Create recurring-task-deployment.yaml Helm template (deployment + service) in k8s/helm/todo-chatbot/templates/recurring-task-deployment.yaml
- [ ] T012 [P] Create realtime-sync-deployment.yaml Helm template (deployment + service) in k8s/helm/todo-chatbot/templates/realtime-sync-deployment.yaml
- [ ] T013 [P] Create reminder-deployment.yaml Helm template (deployment + service) in k8s/helm/todo-chatbot/templates/reminder-deployment.yaml
- [ ] T014 [P] Create audit-deployment.yaml Helm template (deployment + service) in k8s/helm/todo-chatbot/templates/audit-deployment.yaml
- [ ] T015 Create dapr-components.yaml Helm template (PubSub + StateStore from values) in k8s/helm/todo-chatbot/templates/dapr-components.yaml
- [ ] T016 Create infrastructure.yaml Helm template (conditional Redpanda + Redis for local) in k8s/helm/todo-chatbot/templates/infrastructure.yaml
- [ ] T017 Bump Chart.yaml version to 0.2.0 in k8s/helm/todo-chatbot/Chart.yaml
- [ ] T018 Run helm lint to validate chart syntax in k8s/helm/todo-chatbot/
- [ ] T019 Run helm template dry-run to verify all 6 deployments render correctly

**Checkpoint**: All Dockerfiles build, Helm chart lints and renders all services correctly.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Environment-specific configuration that MUST be complete before any deployment

**⚠️ CRITICAL**: No deployment can begin until this phase is complete

### Environment Values Files

- [ ] T020 Create values-local.yaml with Minikube-specific overrides (local broker URLs, IfNotPresent pullPolicy, 1 replica) in k8s/helm/todo-chatbot/values-local.yaml
- [ ] T021 Create values-cloud.yaml with DOKS-specific overrides (GHCR image repos, Redpanda Cloud URLs, SASL auth, 2 replicas) in k8s/helm/todo-chatbot/values-cloud.yaml
- [ ] T022 Validate environment separation by diffing helm template output for local vs cloud values
- [ ] T023 Create Dapr component templates that read broker/state config from Helm values in k8s/helm/todo-chatbot/templates/dapr-components.yaml

**Checkpoint**: Foundation ready - local and cloud deployments can now proceed independently.

---

## Phase 3: User Story 1 - Local Deployment on Minikube (Priority: P1) 🎯 MVP

**Goal**: Deploy complete system on Minikube with all services, Dapr sidecars, Redpanda, and Redis

**Independent Test**: Start Minikube, deploy, open frontend, create a recurring task, complete it, verify next occurrence auto-created

### Minikube Setup

- [ ] T024 [US1] Start Minikube cluster with adequate resources (4 CPUs, 8GB RAM, Docker driver)
- [ ] T025 [US1] Install Dapr on Minikube cluster and verify all Dapr system pods are running
- [ ] T026 [US1] Apply Dapr component configurations (pubsub, statestore, secrets, cron) to cluster from dapr/components/

### Image Building

- [ ] T027 [P] [US1] Build todo-backend image on Minikube Docker daemon
- [ ] T028 [P] [US1] Build todo-frontend image on Minikube Docker daemon
- [ ] T029 [P] [US1] Build recurring-task-service image on Minikube Docker daemon
- [ ] T030 [P] [US1] Build realtime-sync-service image on Minikube Docker daemon
- [ ] T031 [P] [US1] Build reminder-service image on Minikube Docker daemon
- [ ] T032 [P] [US1] Build audit-service image on Minikube Docker daemon

### Deployment

- [ ] T033 [US1] Create Kubernetes secrets for local environment (DATABASE_URL, JWT_SECRET)
- [ ] T034 [US1] Deploy full stack with Helm using values-local.yaml via helm upgrade --install
- [ ] T035 [US1] Verify all 6 service pods are Running with 2/2 containers (app + Dapr sidecar)
- [ ] T036 [US1] Verify Dapr dashboard shows all components (pubsub, statestore) as healthy

### Smoke Test

- [ ] T037 [US1] Access frontend via minikube service and verify page loads
- [ ] T038 [US1] Create a task via the UI and verify it persists in the database
- [ ] T039 [US1] Create a recurring task, mark complete, verify next occurrence created within 5 seconds
- [ ] T040 [US1] Verify audit service logged the task creation and completion events

**Checkpoint**: User Story 1 (Local Minikube) is fully functional - complete system running locally with Dapr.

---

## Phase 4: User Story 2 - Cloud Deployment to Managed Kubernetes (Priority: P1)

**Goal**: Deploy to DOKS with Redpanda Cloud and externalized secrets

**Independent Test**: Deploy to DOKS, access frontend via public URL, create task, verify Dapr events flow through Redpanda Cloud

### Cloud Cluster Setup

- [ ] T041 [US2] Create DOKS cluster with doctl (3 nodes, s-2vcpu-4gb) or equivalent managed K8s
- [ ] T042 [US2] Install Dapr on cloud cluster and verify Dapr system pods are running
- [ ] T043 [US2] Provision Redpanda Cloud Serverless topics (task-events, reminders, task-updates)

### Secrets and Configuration

- [ ] T044 [US2] Create Kubernetes secret todo-secrets with DATABASE_URL, JWT_SECRET, COHERE_API_KEY
- [ ] T045 [US2] Create Kubernetes secret redpanda-auth with SASL_USERNAME, SASL_PASSWORD
- [ ] T046 [US2] Update values-cloud.yaml with real Redpanda Cloud bootstrap URLs in k8s/helm/todo-chatbot/values-cloud.yaml
- [ ] T047 [US2] Update values-cloud.yaml with real GHCR image repository paths in k8s/helm/todo-chatbot/values-cloud.yaml

### Image Push

- [ ] T048 [P] [US2] Build and push todo-backend image to GHCR with commit tag
- [ ] T049 [P] [US2] Build and push todo-frontend image to GHCR with commit tag
- [ ] T050 [P] [US2] Build and push recurring-task-service image to GHCR with commit tag
- [ ] T051 [P] [US2] Build and push realtime-sync-service image to GHCR with commit tag
- [ ] T052 [P] [US2] Build and push reminder-service image to GHCR with commit tag
- [ ] T053 [P] [US2] Build and push audit-service image to GHCR with commit tag

### Cloud Deployment

- [ ] T054 [US2] Deploy to cloud cluster with Helm using values-cloud.yaml
- [ ] T055 [US2] Verify all 6 service pods are Running with Dapr sidecars on cloud cluster
- [ ] T056 [US2] Verify no hard-coded secrets in any deployed container by inspecting env vars
- [ ] T057 [US2] Verify Redpanda Cloud shows connected consumers for all 3 topics

### Smoke Test

- [ ] T058 [US2] Access frontend via cloud external URL and verify page loads
- [ ] T059 [US2] Create a task, complete it, verify end-to-end flow through Redpanda Cloud
- [ ] T060 [US2] Verify changing Redpanda Cloud broker URL only requires updating Dapr component config (no code changes)

**Checkpoint**: User Story 2 (Cloud Deployment) is fully functional - system running on managed K8s with Redpanda Cloud.

---

## Phase 5: User Story 3 - Automated CI/CD Pipeline (Priority: P2)

**Goal**: GitHub Actions pipeline that builds, pushes, and deploys automatically on push to main

**Independent Test**: Push a code change to main, verify pipeline builds images, pushes to GHCR, deploys to K8s, and services update

### Workflow Foundation

- [ ] T061 [US3] Create .github/workflows/ directory structure
- [ ] T062 [US3] Create deploy.yml workflow file with trigger on push to main and PR to main in .github/workflows/deploy.yml
- [ ] T063 [US3] Implement change detection job using dorny/paths-filter in .github/workflows/deploy.yml

### Build Stage

- [ ] T064 [US3] Implement build job with matrix strategy (per changed service) in .github/workflows/deploy.yml
- [ ] T065 [US3] Configure Docker build step to tag images with commit SHA and latest in .github/workflows/deploy.yml
- [ ] T066 [US3] Configure GHCR login step using GITHUB_TOKEN in .github/workflows/deploy.yml

### Push Stage

- [ ] T067 [US3] Implement image push step to GHCR (SHA + latest tags) in .github/workflows/deploy.yml
- [ ] T068 [US3] Add condition to skip push on pull request events in .github/workflows/deploy.yml

### Deploy Stage

- [ ] T069 [US3] Implement kubeconfig setup from KUBE_CONFIG secret in .github/workflows/deploy.yml
- [ ] T070 [US3] Implement secret creation/update step from GitHub Actions secrets in .github/workflows/deploy.yml
- [ ] T071 [US3] Implement helm upgrade step with values-cloud.yaml and image tag overrides in .github/workflows/deploy.yml
- [ ] T072 [US3] Add kubectl rollout status verification with 300s timeout in .github/workflows/deploy.yml
- [ ] T073 [US3] Add condition to only deploy on push to main (not PRs) in .github/workflows/deploy.yml

### Failure Handling

- [ ] T074 [US3] Configure fail-fast on build job failures in .github/workflows/deploy.yml
- [ ] T075 [US3] Add rollback step on deploy failure (helm rollback) in .github/workflows/deploy.yml

### Validation

- [ ] T076 [US3] Test pipeline on feature branch to verify build-only (no deploy) behavior
- [ ] T077 [US3] Test pipeline on main branch to verify full build-push-deploy cycle
- [ ] T078 [US3] Verify pipeline fails fast and reports clear errors when build fails

**Checkpoint**: User Story 3 (CI/CD) is fully functional - pushes to main auto-deploy to cloud cluster.

---

## Phase 6: User Story 4 - Monitoring and Observability (Priority: P2)

**Goal**: Structured logs, health visibility, and broker monitoring across all services

**Independent Test**: Trigger task creation, verify structured JSON logs visible via kubectl, correlation IDs trace across services, health endpoints respond

### Structured Logging

- [ ] T079 [P] [US4] Configure JSON structured log formatter for backend in backend/src/main.py
- [ ] T080 [P] [US4] Configure JSON structured log formatter for recurring-task-service in services/recurring-task-service/src/main.py
- [ ] T081 [P] [US4] Configure JSON structured log formatter for realtime-sync-service in services/realtime-sync-service/src/main.py
- [ ] T082 [P] [US4] Configure JSON structured log formatter for reminder-service in services/reminder-service/src/main.py
- [ ] T083 [P] [US4] Configure JSON structured log formatter for audit-service in services/audit-service/src/main.py

### Health Endpoint Verification

- [ ] T084 [US4] Verify backend /health endpoint returns 200 with dependency status (database, Dapr)
- [ ] T085 [US4] Verify all 4 microservice /health endpoints return 200 with service name

### Correlation ID Tracing

- [ ] T086 [US4] Verify correlation IDs persist across backend → Dapr Pub/Sub → microservice logs
- [ ] T087 [US4] Document correlation ID tracing procedure with example in specs/010-deployment-production-readiness/

### Broker Visibility

- [ ] T088 [US4] Access Redpanda Console and verify consumer group visibility for all 3 topics
- [ ] T089 [US4] Verify Dapr dashboard shows Pub/Sub component with topic subscription status

**Checkpoint**: User Story 4 (Monitoring) is fully functional - logs are structured, traceable, and broker is visible.

---

## Phase 7: User Story 5 - Environment Parity (Priority: P3)

**Goal**: Local and cloud deployments mirror each other structurally

**Independent Test**: Compare local and cloud Helm rendered manifests - only values differ, not structure

### Parity Verification

- [ ] T090 [US5] Compare helm template output for values-local.yaml vs values-cloud.yaml and document structural differences
- [ ] T091 [US5] Verify same Dapr component types (pubsub.kafka, state.redis) used in both environments
- [ ] T092 [US5] Verify adding a new microservice follows identical Helm template pattern in both environments
- [ ] T093 [US5] Document environment-specific values that differ between local and cloud in specs/010-deployment-production-readiness/

**Checkpoint**: User Story 5 (Parity) verified - environments are structurally equivalent.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and hardening

### Documentation

- [ ] T094 [P] Update quickstart.md with verified deployment steps in specs/010-deployment-production-readiness/quickstart.md
- [ ] T095 [P] Document rollback procedure (helm rollback command and verification steps)
- [ ] T096 [P] Document GitHub Actions secret configuration procedure
- [ ] T097 Document troubleshooting guide for common deployment failures

### Final Validation

- [ ] T098 Run full CI/CD end-to-end test: push change → auto-deploy → verify services updated
- [ ] T099 Verify all 8 success criteria from spec.md are met
- [ ] T100 Run helm lint on final chart in k8s/helm/todo-chatbot/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 Helm chart tasks (T007-T017)
- **User Story 1 (Phase 3)**: Depends on Phase 2 - local values file ready
- **User Story 2 (Phase 4)**: Depends on Phase 2 - cloud values file ready
  - Can run in parallel with US1 if Dockerfiles (Phase 1) are complete
- **User Story 3 (Phase 5)**: Depends on Phase 4 - cloud deployment must exist first
- **User Story 4 (Phase 6)**: Depends on Phase 3 or 4 - needs running deployment
- **User Story 5 (Phase 7)**: Depends on Phase 3 AND Phase 4 - needs both environments
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

| Story | Priority | Dependencies | Can Parallel With |
|-------|----------|--------------|-------------------|
| US1 - Local Minikube | P1 | Phase 2 only | US2 (after Dockerfiles) |
| US2 - Cloud DOKS | P1 | Phase 2 + Dockerfiles | US1 |
| US3 - CI/CD Pipeline | P2 | US2 (needs cloud cluster) | US4 |
| US4 - Monitoring | P2 | US1 or US2 (needs running deployment) | US3 |
| US5 - Environment Parity | P3 | US1 AND US2 (needs both environments) | None |

### Within Each User Story

- Setup/config before deployment
- Deployment before verification
- Verification before smoke test

### Parallel Opportunities

- T001-T006 (all Dockerfiles) can run in parallel
- T011-T014 (microservice Helm templates) can run in parallel
- T027-T032 (local image builds) can run in parallel
- T048-T053 (GHCR image pushes) can run in parallel
- T079-T083 (JSON log configuration) can run in parallel
- T094-T096 (documentation tasks) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Build all 6 images in parallel (T027-T032):
Task: "Build todo-backend image on Minikube Docker daemon"
Task: "Build todo-frontend image on Minikube Docker daemon"
Task: "Build recurring-task-service image on Minikube Docker daemon"
Task: "Build realtime-sync-service image on Minikube Docker daemon"
Task: "Build reminder-service image on Minikube Docker daemon"
Task: "Build audit-service image on Minikube Docker daemon"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Dockerfiles + Helm Chart
2. Complete Phase 2: Environment Values
3. Complete Phase 3: Local Minikube Deployment (US1)
4. **STOP and VALIDATE**: Full system running locally with Dapr
5. Demo the local deployment

### Incremental Delivery

1. Setup + Foundational → Helm chart ready
2. Add US1 (Local) → Test independently → Demo (MVP!)
3. Add US2 (Cloud) → Test independently → Deploy to real users
4. Add US3 (CI/CD) → Test independently → Automated deployments
5. Add US4 (Monitoring) → Test independently → Observable system
6. Add US5 (Parity) → Verify → Production-ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Local Minikube)
   - Developer B: US2 (Cloud DOKS)
3. After US2 completes:
   - Developer A: US3 (CI/CD)
   - Developer B: US4 (Monitoring)
4. US5 (Parity) after both US1 and US2 verified

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable at its checkpoint
- 100 total tasks across 8 phases
- 30 tasks marked [P] for parallel execution
- Commit after each task or logical group
