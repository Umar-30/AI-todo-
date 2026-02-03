# Tasks: Phase IV - Local Kubernetes Deployment

**Input**: Design documents from `/specs/008-local-k8s-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No tests explicitly requested. Validation via `helm lint`, `kubectl --dry-run`, and smoke tests.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Exact file paths included in descriptions

## Path Conventions

Infrastructure artifacts in `k8s/` directory:
- `k8s/docker/` - Dockerfiles and nginx config
- `k8s/manifests/` - Raw Kubernetes manifests
- `k8s/helm/todo-chatbot/` - Helm chart

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and verify prerequisites

- [x] T001 Create k8s directory structure: k8s/docker/, k8s/manifests/, k8s/helm/todo-chatbot/templates/
- [x] T002 [P] Create .dockerignore file at k8s/docker/.dockerignore
- [x] T003 [P] Create .helmignore file at k8s/helm/todo-chatbot/.helmignore
- [x] T004 Verify Minikube, kubectl, helm, and Docker are installed (document in k8s/README.md)

**Checkpoint**: Directory structure ready for artifact creation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared configuration that all user stories depend on

**Critical**: No user story work can begin until this phase is complete

- [x] T005 Create nginx configuration for frontend at k8s/docker/nginx.conf
- [x] T006 Create ConfigMap manifest at k8s/manifests/configmap.yaml
- [x] T007 [P] Add health endpoint to backend at backend/src/health.py (if not exists) - ALREADY EXISTS

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Containerize Application Components (Priority: P1)

**Goal**: Build Docker images for frontend and backend that work with Minikube

**Independent Test**: Build images and run with `docker run` to verify application starts

### Implementation for User Story 1

- [x] T008 [P] [US1] Create backend Dockerfile at k8s/docker/backend.Dockerfile (multi-stage, python:3.11-slim)
- [x] T009 [P] [US1] Create frontend Dockerfile at k8s/docker/frontend.Dockerfile (multi-stage, node:20-alpine + nginx:alpine)
- [ ] T010 [US1] Build backend image: `docker build -t todo-backend:latest -f k8s/docker/backend.Dockerfile .`
- [ ] T011 [US1] Build frontend image: `docker build -t todo-frontend:latest -f k8s/docker/frontend.Dockerfile .`
- [ ] T012 [US1] Verify backend container runs: `docker run -p 8000:8000 todo-backend:latest`
- [ ] T013 [US1] Verify frontend container runs: `docker run -p 3000:3000 todo-frontend:latest`
- [ ] T014 [US1] Load images into Minikube: `minikube image load todo-backend:latest todo-frontend:latest`

**Checkpoint**: Container images built and verified locally - can run with Docker

---

## Phase 4: User Story 2 - Deploy to Minikube Cluster (Priority: P2)

**Goal**: Deploy containers to Minikube using raw Kubernetes manifests

**Independent Test**: Apply manifests and verify pods running, services accessible

**Depends on**: US1 (container images must exist)

### Implementation for User Story 2

- [x] T015 [P] [US2] Create backend Deployment manifest at k8s/manifests/backend-deployment.yaml
- [x] T016 [P] [US2] Create backend Service manifest at k8s/manifests/backend-service.yaml
- [x] T017 [P] [US2] Create frontend Deployment manifest at k8s/manifests/frontend-deployment.yaml
- [x] T018 [P] [US2] Create frontend Service manifest at k8s/manifests/frontend-service.yaml
- [ ] T019 [US2] Validate manifests with dry-run: `kubectl apply --dry-run=client -f k8s/manifests/`
- [ ] T020 [US2] Apply ConfigMap: `kubectl apply -f k8s/manifests/configmap.yaml`
- [ ] T021 [US2] Apply backend resources: `kubectl apply -f k8s/manifests/backend-deployment.yaml -f k8s/manifests/backend-service.yaml`
- [ ] T022 [US2] Apply frontend resources: `kubectl apply -f k8s/manifests/frontend-deployment.yaml -f k8s/manifests/frontend-service.yaml`
- [ ] T023 [US2] Verify pods running: `kubectl get pods -l app.kubernetes.io/name=todo-chatbot`
- [ ] T024 [US2] Verify services created: `kubectl get svc`
- [ ] T025 [US2] Access frontend via NodePort: `minikube service todo-frontend-svc`
- [ ] T026 [US2] Test scaling: `kubectl scale deployment todo-backend --replicas=3`

**Checkpoint**: Application running on Minikube via raw manifests

---

## Phase 5: User Story 3 - Package with Helm Charts (Priority: P3)

**Goal**: Create Helm chart for configurable, versioned deployment

**Independent Test**: Run `helm lint` and `helm install` on fresh cluster

**Depends on**: US2 (manifests validated and working)

### Implementation for User Story 3

- [x] T027 [US3] Create Chart.yaml at k8s/helm/todo-chatbot/Chart.yaml
- [x] T028 [US3] Create values.yaml at k8s/helm/todo-chatbot/values.yaml
- [x] T029 [US3] Create _helpers.tpl at k8s/helm/todo-chatbot/templates/_helpers.tpl
- [x] T030 [P] [US3] Create backend-deployment.yaml template at k8s/helm/todo-chatbot/templates/backend-deployment.yaml
- [x] T031 [P] [US3] Create backend-service.yaml template at k8s/helm/todo-chatbot/templates/backend-service.yaml
- [x] T032 [P] [US3] Create frontend-deployment.yaml template at k8s/helm/todo-chatbot/templates/frontend-deployment.yaml
- [x] T033 [P] [US3] Create frontend-service.yaml template at k8s/helm/todo-chatbot/templates/frontend-service.yaml
- [x] T034 [P] [US3] Create configmap.yaml template at k8s/helm/todo-chatbot/templates/configmap.yaml
- [x] T035 [US3] Create NOTES.txt at k8s/helm/todo-chatbot/templates/NOTES.txt
- [ ] T036 [US3] Run helm lint: `helm lint k8s/helm/todo-chatbot`
- [ ] T037 [US3] Uninstall raw manifests: `kubectl delete -f k8s/manifests/`
- [ ] T038 [US3] Install Helm chart: `helm install todo-chatbot k8s/helm/todo-chatbot`
- [ ] T039 [US3] Verify Helm release: `helm list`
- [ ] T040 [US3] Test helm upgrade: `helm upgrade todo-chatbot k8s/helm/todo-chatbot --set backend.replicas=2`
- [ ] T041 [US3] Test helm uninstall: `helm uninstall todo-chatbot`

**Checkpoint**: Helm chart validated - can install/upgrade/uninstall cleanly

---

## Phase 6: User Story 4 - AI-Assisted DevOps Workflow (Priority: P4)

**Goal**: Document AI tool usage with CLI fallbacks

**Independent Test**: Use each AI tool and verify useful output

**Depends on**: US1-US3 (all deployment artifacts exist)

### Implementation for User Story 4

- [x] T042 [P] [US4] Document Docker AI (Gordon) usage in k8s/docs/ai-tools.md
- [x] T043 [P] [US4] Document kubectl-ai usage in k8s/docs/ai-tools.md
- [x] T044 [P] [US4] Document Kagent usage in k8s/docs/ai-tools.md
- [x] T045 [US4] Add CLI fallback commands to k8s/docs/ai-tools.md
- [ ] T046 [US4] Test Docker AI: `docker ai "Explain the backend Dockerfile"`
- [ ] T047 [US4] Test kubectl-ai: `kubectl-ai "Show pod status for todo-chatbot"`
- [ ] T048 [US4] Test Kagent: `kagent "Analyze cluster health"`
- [ ] T049 [US4] Verify all operations work without AI tools (CLI only)

**Checkpoint**: AI tools documented with working CLI fallbacks

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation and validation

- [x] T050 Update k8s/README.md with complete deployment instructions
- [x] T051 [P] Add troubleshooting section to k8s/docs/troubleshooting.md
- [ ] T052 [P] Validate quickstart.md steps work end-to-end
- [ ] T053 Run final validation checklist from plan.md
- [ ] T054 Clean up any temporary resources from testing

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
     │
     ▼
Phase 2 (Foundational) ──── BLOCKS ALL USER STORIES
     │
     ▼
Phase 3 (US1: Containers) ◄─── MVP
     │
     ▼
Phase 4 (US2: K8s Deploy) ◄─── Requires US1 images
     │
     ▼
Phase 5 (US3: Helm) ◄─── Requires US2 manifests
     │
     ▼
Phase 6 (US4: AI Tools) ◄─── Requires all artifacts
     │
     ▼
Phase 7 (Polish)
```

### User Story Dependencies

| Story | Depends On | Blocks |
|-------|------------|--------|
| US1 (Containers) | Phase 2 | US2 |
| US2 (K8s Deploy) | US1 | US3 |
| US3 (Helm) | US2 | US4 |
| US4 (AI Tools) | US1-US3 | None |

### Within Each User Story

1. Create files (parallelizable where marked [P])
2. Validate/lint artifacts
3. Apply/deploy
4. Verify functionality

---

## Parallel Execution Examples

### Phase 1 (Setup) - All parallel

```bash
# Launch all setup tasks together:
Task: T002 "Create .dockerignore"
Task: T003 "Create .helmignore"
```

### Phase 3 (US1) - Dockerfiles parallel

```bash
# Launch both Dockerfiles together:
Task: T008 "Create backend Dockerfile"
Task: T009 "Create frontend Dockerfile"
```

### Phase 4 (US2) - Manifests parallel

```bash
# Launch all manifest creation together:
Task: T015 "Create backend-deployment.yaml"
Task: T016 "Create backend-service.yaml"
Task: T017 "Create frontend-deployment.yaml"
Task: T018 "Create frontend-service.yaml"
```

### Phase 5 (US3) - Templates parallel

```bash
# Launch all Helm templates together:
Task: T030 "Create backend-deployment template"
Task: T031 "Create backend-service template"
Task: T032 "Create frontend-deployment template"
Task: T033 "Create frontend-service template"
Task: T034 "Create configmap template"
```

### Phase 6 (US4) - Documentation parallel

```bash
# Launch all AI tool documentation together:
Task: T042 "Document Docker AI"
Task: T043 "Document kubectl-ai"
Task: T044 "Document Kagent"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T007)
3. Complete Phase 3: User Story 1 (T008-T014)
4. **STOP and VALIDATE**: Docker images build and run locally
5. Demo: Show containers running with `docker run`

### Incremental Delivery

1. **MVP**: Setup + Foundational + US1 → Containers work locally
2. **+US2**: Add Kubernetes deployment → App runs on Minikube
3. **+US3**: Add Helm packaging → Configurable deployment
4. **+US4**: Add AI tooling docs → Enhanced developer experience
5. **Polish**: Final docs and validation

### Single Developer Strategy

Execute phases sequentially: 1 → 2 → 3 → 4 → 5 → 6 → 7

Estimated execution: ~2-3 hours total

---

## Notes

- [P] tasks = different files, no dependencies
- [US#] label maps task to specific user story
- US1 is the MVP - stop and validate after completion
- All AI tool tasks have CLI fallbacks
- Minikube must be running for US2+ tasks
- Run `eval $(minikube docker-env)` before building images
