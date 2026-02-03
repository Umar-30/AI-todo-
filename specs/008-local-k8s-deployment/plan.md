# Implementation Plan: Phase IV - Local Kubernetes Deployment

**Branch**: `008-local-k8s-deployment` | **Date**: 2026-02-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-local-k8s-deployment/spec.md`

## Summary

Deploy the Phase III Todo Chatbot (FastAPI backend + React/Vite frontend) to a local Minikube cluster using Docker containers, Kubernetes manifests, and Helm charts. Leverage AI-assisted DevOps tools (Docker AI Gordon, kubectl-ai, Kagent) to accelerate development while maintaining fallback to standard CLI operations.

## Technical Context

**Language/Version**: Dockerfile (multi-stage), YAML (Kubernetes/Helm), Bash scripts
**Primary Dependencies**: Docker Desktop, Minikube, Helm 3.x, kubectl
**Storage**: External (Neon PostgreSQL - not containerized, accessed via DATABASE_URL)
**Testing**: `helm lint`, `kubectl --dry-run`, container smoke tests
**Target Platform**: Local Minikube cluster (Kubernetes 1.28+)
**Project Type**: Infrastructure/DevOps (deploying existing web application)
**Performance Goals**: Build images in <5 minutes, deploy via Helm in <3 minutes
**Constraints**: Local-only, no cloud providers, beginner-friendly
**Scale/Scope**: 2 services (frontend, backend), 1-5 replicas each

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| VII. Non-Implementation | PASS | No Phase III app logic modified; infrastructure-only |
| VIII. AI-First Tooling | PASS | Docker AI, kubectl-ai, Kagent preferred; CLI fallback documented |
| IX. Local-Only Deployment | PASS | Minikube only; no cloud providers |
| X. Spec-Driven Infrastructure | PASS | All resources defined as specs before generation |
| XI. Beginner-Friendly Simplicity | PASS | Simple patterns; extensive documentation |
| XII. Structured Output | PASS | Reproducible Dockerfiles, manifests, Helm charts |
| XIII. AIOps Alignment | PASS | AI tools for generation, health analysis, debugging |

**Gate Status**: PASSED - Proceeding to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/008-local-k8s-deployment/
├── plan.md              # This file
├── research.md          # Phase 0: Tool research and best practices
├── data-model.md        # Phase 1: Infrastructure entities and relationships
├── quickstart.md        # Phase 1: Step-by-step deployment guide
├── contracts/           # Phase 1: Kubernetes manifest specs
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   └── frontend-service.yaml
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Infrastructure Artifacts (repository root)

```text
k8s/
├── docker/
│   ├── backend.Dockerfile      # Multi-stage Python/FastAPI image
│   └── frontend.Dockerfile     # Multi-stage Node/Nginx image
├── manifests/
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   └── configmap.yaml
└── helm/
    └── todo-chatbot/
        ├── Chart.yaml
        ├── values.yaml
        ├── templates/
        │   ├── _helpers.tpl
        │   ├── backend-deployment.yaml
        │   ├── backend-service.yaml
        │   ├── frontend-deployment.yaml
        │   ├── frontend-service.yaml
        │   ├── configmap.yaml
        │   └── NOTES.txt
        └── .helmignore
```

**Structure Decision**: Infrastructure artifacts placed in `k8s/` directory at repository root, separate from application source code in `backend/` and `frontend/`.

## Complexity Tracking

No constitution violations requiring justification.

---

## Phase 0: Research & Tool Analysis

See [research.md](./research.md) for detailed findings.

### Key Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Container Runtime | Docker Desktop with Minikube | Standard local K8s development setup |
| Image Registry | Minikube's built-in Docker daemon | Simplest for local development; no registry needed |
| Helm Version | Helm 3.x | No Tiller required; simpler security model |
| Service Exposure | NodePort + minikube tunnel | Standard approach for local access |
| AI Tooling | Gordon, kubectl-ai, Kagent | Per constitution; CLI fallback always available |

---

## Phase 1: Infrastructure Design

### 1.1 Container Images

#### Backend (FastAPI/Python)

```dockerfile
# Dockerfile.backend - Multi-stage build
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY backend/src ./src
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend (React/Vite/Nginx)

```dockerfile
# Dockerfile.frontend - Multi-stage build
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY k8s/docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://localhost:3000 || exit 1
CMD ["nginx", "-g", "daemon off;"]
```

### 1.2 Kubernetes Resources

See [contracts/](./contracts/) for full manifest specifications.

#### Resource Summary

| Resource | Name | Type | Ports | Replicas |
|----------|------|------|-------|----------|
| Backend Deployment | todo-backend | Deployment | 8000 | 1-5 |
| Backend Service | todo-backend-svc | ClusterIP | 8000 | - |
| Frontend Deployment | todo-frontend | Deployment | 3000 | 1-5 |
| Frontend Service | todo-frontend-svc | NodePort | 3000:30080 | - |
| ConfigMap | todo-config | ConfigMap | - | - |

### 1.3 Helm Chart Structure

```yaml
# Chart.yaml
apiVersion: v2
name: todo-chatbot
description: Phase III Todo Chatbot deployed to Kubernetes
type: application
version: 0.1.0
appVersion: "1.0.0"
```

```yaml
# values.yaml (configurable parameters)
backend:
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  replicas: 1
  port: 8000
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

frontend:
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  replicas: 1
  port: 3000
  nodePort: 30080
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 200m
      memory: 256Mi

config:
  databaseUrl: ""  # Set via --set or values override
  apiBaseUrl: "http://todo-backend-svc:8000"
```

---

## Deployment Workflow

### Step 1: Prerequisites Setup

```bash
# Verify installations
docker --version
minikube version
kubectl version --client
helm version

# Start Minikube
minikube start --driver=docker --cpus=2 --memory=4096

# Configure Docker to use Minikube's daemon
eval $(minikube docker-env)
```

### Step 2: Build Container Images

```bash
# Using Docker AI (Gordon) - preferred
docker ai "Build a multi-stage Dockerfile for the FastAPI backend in backend/"

# OR standard CLI fallback
docker build -t todo-backend:latest -f k8s/docker/backend.Dockerfile .
docker build -t todo-frontend:latest -f k8s/docker/frontend.Dockerfile .
```

### Step 3: Deploy with Helm

```bash
# Using kubectl-ai - preferred
kubectl-ai "Deploy the todo-chatbot helm chart with 2 backend replicas"

# OR standard CLI fallback
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  --set backend.replicas=2 \
  --set config.databaseUrl="$DATABASE_URL"
```

### Step 4: Verify Deployment

```bash
# Using Kagent - preferred
kagent "Analyze health of todo-chatbot deployment"

# OR standard CLI fallback
kubectl get pods -l app.kubernetes.io/name=todo-chatbot
kubectl get services
minikube service todo-frontend-svc --url
```

### Step 5: Access Application

```bash
# Open frontend in browser
minikube service todo-frontend-svc

# OR use tunnel for stable URL
minikube tunnel
# Access at http://localhost:30080
```

---

## AI Tool Usage Guide

### Docker AI (Gordon)

| Task | AI Command | CLI Fallback |
|------|------------|--------------|
| Generate Dockerfile | `docker ai "Create Dockerfile for FastAPI app"` | Write manually |
| Explain Dockerfile | `docker ai "Explain this Dockerfile"` | Read documentation |
| Optimize image | `docker ai "Reduce image size for backend"` | Multi-stage builds |
| Debug build | `docker ai "Why is my build failing?"` | `docker build --progress=plain` |

### kubectl-ai

| Task | AI Command | CLI Fallback |
|------|------------|--------------|
| Deploy | `kubectl-ai "Deploy backend with 3 replicas"` | `kubectl apply -f` |
| Scale | `kubectl-ai "Scale frontend to 2 pods"` | `kubectl scale deployment` |
| Debug | `kubectl-ai "Why is my pod crashing?"` | `kubectl describe pod` |
| Logs | `kubectl-ai "Show backend logs"` | `kubectl logs -l app=backend` |

### Kagent

| Task | AI Command | CLI Fallback |
|------|------------|--------------|
| Health check | `kagent "Check cluster health"` | `kubectl get all` |
| Optimize | `kagent "Suggest resource optimizations"` | Manual analysis |
| Troubleshoot | `kagent "Diagnose networking issues"` | `kubectl exec` + `curl` |

---

## Validation Checklist

- [ ] Docker images build successfully
- [ ] Images load into Minikube
- [ ] Pods reach Running state
- [ ] Services route traffic correctly
- [ ] Frontend accessible via NodePort
- [ ] Backend health endpoint responds
- [ ] Helm lint passes
- [ ] Helm install/upgrade/uninstall work
- [ ] Scaling works (1-5 replicas)
- [ ] All operations work with CLI fallback

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks in priority order (P1 → P4)
3. Validate each user story independently
4. Document any issues in troubleshooting guide
