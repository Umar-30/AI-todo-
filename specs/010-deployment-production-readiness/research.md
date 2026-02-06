# Research: Deployment & Production Readiness

**Feature**: 010-deployment-production-readiness
**Date**: 2026-02-06

## Phase 0 Research Findings

### R1: Container Registry Selection

**Decision**: GitHub Container Registry (GHCR)

**Rationale**: GHCR integrates natively with GitHub Actions (same auth, same ecosystem). Free for public repos, generous free tier for private. Eliminates need for external registry credentials.

**Alternatives considered**:
- Docker Hub: Rate limiting on free tier; separate auth setup needed
- DigitalOcean Container Registry: Only useful if targeting DOKS; vendor lock-in
- AWS ECR / GCP Artifact Registry: Over-engineered for this project

---

### R2: Cloud Kubernetes Provider

**Decision**: DigitalOcean Kubernetes (DOKS)

**Rationale**: Simplest managed K8s with lowest cost for small projects. Straightforward `doctl` CLI integration. DOKS supports Dapr installation via Helm. Good fit for a hackathon/learning project.

**Alternatives considered**:
- GKE: More features but more complex setup, higher baseline cost
- AKS: Excellent Dapr support (Microsoft owns Dapr) but Azure onboarding is heavier
- All three are structurally equivalent for this workload; DOKS chosen for simplicity

---

### R3: Dapr Installation Method on K8s

**Decision**: Helm-based Dapr installation (`dapr init -k` or Helm chart)

**Rationale**: `dapr init -k` uses Helm under the hood. Helm gives explicit version control and declarative configuration. Works identically on Minikube and DOKS.

**Alternatives considered**:
- Dapr CLI standalone: Less control, harder to reproduce
- Operator pattern: Over-complex for current scale

---

### R4: Environment Configuration Strategy

**Decision**: Helm values overlay files (`values-local.yaml`, `values-cloud.yaml`)

**Rationale**: Helm's `--values` flag allows stacking configuration. Base `values.yaml` contains defaults. Environment-specific files override only what differs (broker URLs, resource limits, image registry). Same templates, different values.

**Alternatives considered**:
- Kustomize overlays: Would require migrating from Helm; unnecessary
- envsubst: Too fragile, no schema validation
- Terraform: Wrong abstraction level for K8s resource configuration

---

### R5: Secret Management Strategy

**Decision**: Kubernetes Secrets + GitHub Actions Secrets

**Rationale**:
- **Local**: Kubernetes secrets created manually or via Helm `--set` during development
- **Cloud**: Kubernetes secrets created by CI/CD from GitHub Actions secrets
- **Never**: Secrets in source code, Dockerfiles, or values files

This is the simplest approach that meets security requirements. Dapr secrets component can optionally abstract the backing store.

**Alternatives considered**:
- HashiCorp Vault: Production-grade but over-complex for this stage
- SOPS (Mozilla): Good for git-encrypted secrets but adds tooling overhead
- Sealed Secrets: Reasonable middle ground, deferred to future phase

---

### R6: CI/CD Pipeline Architecture

**Decision**: Single GitHub Actions workflow with per-service change detection

**Rationale**: A monorepo workflow that detects which services changed (via `paths` filter or `dorny/paths-filter` action) and builds only those. Three stages: Build (parallel per service) → Push → Deploy.

**Alternatives considered**:
- Separate workflow per service: Too many files, harder to coordinate deployments
- ArgoCD GitOps: Superior for production but significant setup overhead
- GitHub Actions + Argo hybrid: Deferred to future phase

---

### R7: Logging Strategy

**Decision**: Structured JSON logs to stdout, collected by Kubernetes default logging

**Rationale**: All Python services already use `logging` with configurable format. Switch to JSON format for machine-parseable logs. Kubernetes captures stdout/stderr natively. `kubectl logs` provides immediate access. No external logging stack needed initially.

**Alternatives considered**:
- EFK Stack (Elasticsearch/Fluentd/Kibana): Production-grade but heavy for MVP
- Loki + Grafana: Lighter alternative, deferred to monitoring expansion phase
- CloudWatch/Stackdriver: Vendor-specific, ties to one cloud provider

---

### R8: Redpanda Cloud Configuration

**Decision**: Redpanda Cloud Serverless with SASL/SCRAM authentication

**Rationale**: Redpanda Cloud Serverless is pay-per-use, no cluster management. Dapr pubsub.kafka component supports SASL authentication via metadata. Same Dapr component type (`pubsub.kafka`) for both local and cloud - only `brokers` and auth metadata differ.

**Alternatives considered**:
- Redpanda Dedicated: Unnecessary cost for project scale
- Confluent Cloud: More expensive, same Kafka protocol compatibility
- Self-managed Redpanda on K8s (cloud): Defeats the purpose of managed service

---

### R9: Missing Dockerfiles

**Decision**: Create Dockerfiles for backend, frontend (if needed), reminder-service, and audit-service

**Rationale**: Currently only `services/recurring-task-service/Dockerfile` and `services/realtime-sync-service/Dockerfile` exist. The backend and remaining services need Dockerfiles for containerized deployment. Backend Dockerfile exists at `AI-todo/Dockerfile` and `AI-todo-new/Dockerfile` but needs to be created in the standard `backend/` path.

---

### R10: Constitution Principle IX Conflict

**Decision**: Amend Principle IX scope for Phase V

**Rationale**: Principle IX ("Local-Only Deployment") was written for Phase IV scope. Phase V explicitly requires cloud deployment as a user requirement. The principle should be scoped to Phase IV, not applied as a global constraint. The constitution's own governance section allows amendments with documented rationale.

**Justification**: The user explicitly requested cloud deployment (DOKS/GKE/AKS) in the Phase V specification input. This is a deliberate scope expansion, not an accidental violation.
