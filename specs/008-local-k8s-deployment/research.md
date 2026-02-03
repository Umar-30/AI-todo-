# Phase 0 Research: Local Kubernetes Deployment

**Feature**: 008-local-k8s-deployment
**Date**: 2026-02-03
**Status**: Complete

## Research Topics

### 1. Minikube Configuration for Local Development

**Decision**: Use Minikube with Docker driver, 2 CPUs, 4GB RAM

**Rationale**:
- Docker driver is most compatible across Windows/Mac/Linux
- 2 CPUs and 4GB RAM sufficient for 2-service deployment
- Built-in Docker daemon eliminates need for external registry

**Alternatives Considered**:
- Kind (Kubernetes in Docker): Faster startup but less feature-complete
- k3d (k3s in Docker): Lightweight but less documentation
- Docker Desktop Kubernetes: Simpler but less configurable

**Best Practices**:
- Always run `eval $(minikube docker-env)` before building images
- Use `minikube tunnel` for stable service access on Windows
- Configure resource limits to prevent local machine slowdown

---

### 2. Docker Multi-Stage Build Patterns

**Decision**: Use two-stage builds for both frontend and backend

**Rationale**:
- Reduces final image size by 60-80%
- Separates build dependencies from runtime
- Follows cloud-native best practices

**Alternatives Considered**:
- Single-stage builds: Simpler but larger images
- Distroless images: Smaller but harder to debug
- Alpine base: Good balance of size and usability

**Best Practices**:
- Backend: python:3.11-slim (debian-based, smaller than full)
- Frontend: node:20-alpine (build) + nginx:alpine (serve)
- Copy only necessary files in final stage
- Use .dockerignore to exclude unnecessary files

---

### 3. Kubernetes Resource Configuration

**Decision**: Use Deployments + Services with resource limits

**Rationale**:
- Deployments provide declarative updates and rollbacks
- Services provide stable networking
- Resource limits prevent runaway containers

**Alternatives Considered**:
- StatefulSets: Not needed for stateless services
- DaemonSets: Not applicable for application workloads
- Ingress: Overkill for local development; NodePort simpler

**Best Practices**:
- Always specify resource requests and limits
- Use readiness probes to prevent traffic to unhealthy pods
- Use liveness probes to restart crashed containers
- Label all resources for easy selection

**Resource Recommendations**:

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Backend | 100m | 500m | 128Mi | 512Mi |
| Frontend | 50m | 200m | 64Mi | 256Mi |

---

### 4. Helm Chart Best Practices

**Decision**: Single chart with configurable values for both services

**Rationale**:
- Simpler than multiple charts
- All configuration in one values.yaml
- Easier to install/upgrade/uninstall

**Alternatives Considered**:
- Separate charts per service: More modular but complex
- Kustomize: Simpler but less powerful
- Raw manifests: No templating or versioning

**Best Practices**:
- Use _helpers.tpl for reusable template functions
- Externalize all environment-specific values
- Include NOTES.txt with post-install instructions
- Version chart independently from app version

---

### 5. AI DevOps Tool Integration

**Decision**: Prefer AI tools with documented CLI fallback

**Rationale**:
- AI tools accelerate common tasks
- CLI fallback ensures all operations work without AI
- Aligns with constitution principle VIII

**Tool Availability**:

| Tool | Purpose | Availability | Fallback |
|------|---------|--------------|----------|
| Docker AI (Gordon) | Dockerfile generation, builds | Docker Desktop 4.x+ | docker CLI |
| kubectl-ai | Deployment, scaling, debugging | Plugin install required | kubectl CLI |
| Kagent | Cluster analysis, optimization | Separate install | kubectl + manual analysis |

**Installation Commands**:

```bash
# kubectl-ai (via krew)
kubectl krew install ai

# Kagent (if available)
# Check https://github.com/kagent for latest install
```

---

### 6. Service Exposure for Local Access

**Decision**: NodePort for frontend, ClusterIP for backend

**Rationale**:
- NodePort exposes frontend directly to host
- Backend only needs cluster-internal access
- Simpler than Ingress for local development

**Alternatives Considered**:
- LoadBalancer: Requires cloud provider or MetalLB
- Ingress: Requires ingress controller setup
- Port-forward: Manual, not persistent

**Access Methods**:

```bash
# Method 1: Minikube service (opens browser)
minikube service todo-frontend-svc

# Method 2: Minikube tunnel (stable localhost access)
minikube tunnel
# Then access http://localhost:30080

# Method 3: Port forward (manual)
kubectl port-forward svc/todo-frontend-svc 3000:3000
```

---

### 7. Environment Configuration

**Decision**: Use ConfigMap for non-sensitive config, external secrets for DATABASE_URL

**Rationale**:
- ConfigMaps are native Kubernetes
- DATABASE_URL contains credentials, passed at deploy time
- Keeps secrets out of version control

**Best Practices**:
- Never hardcode secrets in manifests
- Use `--set config.databaseUrl=$DATABASE_URL` at install time
- Consider Kubernetes Secrets for production (out of scope for local)

---

## Research Summary

All NEEDS CLARIFICATION items resolved. Technical approach validated against:
- Constitution principles (VII-XIII)
- Spec requirements (FR-001 through FR-021)
- Success criteria (SC-001 through SC-008)

**Ready for Phase 1 Design.**
