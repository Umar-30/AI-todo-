# Infrastructure Data Model: Phase IV Kubernetes Deployment

**Feature**: 008-local-k8s-deployment
**Date**: 2026-02-03
**Status**: Complete

## Entity Overview

This document defines the infrastructure entities and their relationships for deploying the Todo Chatbot to local Kubernetes.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Helm Chart                                │
│                     (todo-chatbot)                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  ConfigMap  │    │  Backend    │    │  Frontend   │         │
│  │             │    │  Deployment │    │  Deployment │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         │           ┌──────┴──────┐    ┌──────┴──────┐         │
│         │           │   Backend   │    │  Frontend   │         │
│         │           │   Service   │    │   Service   │         │
│         │           │  (ClusterIP)│    │  (NodePort) │         │
│         │           └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                     ┌──────┴──────┐                            │
│                     │   Pods      │                            │
│                     │ (1-5 each)  │                            │
│                     └─────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │  External Database      │
              │  (Neon PostgreSQL)      │
              │  [Not Containerized]    │
              └─────────────────────────┘
```

---

## Entity Definitions

### 1. Container Image

A packaged application component with all runtime dependencies.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| name | string | Image identifier | `todo-backend`, `todo-frontend` |
| tag | string | Version tag | Semver or `latest` |
| registry | string | Image source | Minikube daemon (local) |
| platform | string | Target architecture | `linux/amd64` |
| size | number | Compressed size | < 500MB recommended |

**States**: building → built → loaded (in Minikube)

**Relationships**:
- Referenced by: Deployment (spec.containers[].image)
- Built from: Dockerfile

---

### 2. Dockerfile

Build instructions for creating a container image.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| path | string | File location | `k8s/docker/*.Dockerfile` |
| stages | array | Build stages | Minimum 2 (builder, runtime) |
| baseImage | string | Parent image | Official images only |
| exposedPorts | array | Network ports | Backend: 8000, Frontend: 3000 |
| healthcheck | object | Health probe config | Required for orchestration |

**Relationships**:
- Produces: Container Image
- Reads from: Application source code

---

### 3. Deployment

Kubernetes resource managing pod replicas and rollout strategy.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| name | string | Resource identifier | `todo-backend`, `todo-frontend` |
| replicas | number | Desired pod count | 1-5 |
| selector | object | Pod selection labels | Must match pod template |
| strategy | string | Update strategy | `RollingUpdate` |
| containers | array | Container specs | 1 per deployment |
| resources | object | CPU/memory limits | Required |
| probes | object | Health checks | Readiness + Liveness |

**States**: pending → available → updating → scaled

**Relationships**:
- Creates: Pods
- References: Container Image, ConfigMap
- Selected by: Service

---

### 4. Service

Kubernetes resource providing stable network endpoint.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| name | string | Resource identifier | `todo-backend-svc`, `todo-frontend-svc` |
| type | string | Service type | `ClusterIP` or `NodePort` |
| port | number | Service port | Backend: 8000, Frontend: 3000 |
| targetPort | number | Container port | Same as port |
| nodePort | number | Host port (NodePort only) | 30080 for frontend |
| selector | object | Pod selection labels | Must match deployment |

**Relationships**:
- Routes to: Pods (via selector)
- Exposed by: Minikube tunnel

---

### 5. ConfigMap

Kubernetes resource storing non-sensitive configuration.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| name | string | Resource identifier | `todo-config` |
| data | object | Key-value pairs | No secrets |
| API_BASE_URL | string | Backend URL | `http://todo-backend-svc:8000` |

**Relationships**:
- Mounted by: Deployment (envFrom or volumeMounts)

---

### 6. Helm Chart

Package containing templated Kubernetes manifests.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| name | string | Chart identifier | `todo-chatbot` |
| version | string | Chart version | Semver |
| appVersion | string | App version | Matches app release |
| values | object | Configurable params | Documented in values.yaml |
| templates | array | Manifest templates | All K8s resources |

**States**: packaged → installed (release) → upgraded → uninstalled

**Relationships**:
- Contains: Deployment, Service, ConfigMap templates
- Produces: Helm Release

---

### 7. Helm Release

An installed instance of a Helm chart.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| name | string | Release identifier | `todo-chatbot` |
| namespace | string | K8s namespace | `default` |
| revision | number | Upgrade count | Increments on upgrade |
| status | string | Release state | deployed, failed, etc. |
| values | object | Applied configuration | Merged from values.yaml + overrides |

**Relationships**:
- Created from: Helm Chart
- Manages: All K8s resources in chart

---

## Validation Rules

### Container Images

- MUST use multi-stage builds
- MUST NOT contain secrets
- MUST include health check endpoint
- MUST be < 500MB compressed

### Deployments

- MUST specify resource requests and limits
- MUST include readiness probe
- MUST include liveness probe
- MUST use labels matching service selectors

### Services

- Backend MUST use ClusterIP (internal only)
- Frontend MUST use NodePort (external access)
- MUST have selector matching deployment labels

### Helm Charts

- MUST pass `helm lint`
- MUST externalize all configuration to values.yaml
- MUST include NOTES.txt with usage instructions

---

## State Transitions

### Deployment Lifecycle

```
[created] → [pending] → [available] → [updating] → [available]
                │                           │
                └── [failed] ◄──────────────┘
```

### Helm Release Lifecycle

```
[install] → [deployed] → [upgrade] → [deployed]
     │           │            │
     └── [failed]└── [uninstall] → [deleted]
```
