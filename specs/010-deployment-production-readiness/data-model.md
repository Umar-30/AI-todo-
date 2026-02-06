# Data Model: Deployment & Production Readiness

**Feature**: 010-deployment-production-readiness
**Date**: 2026-02-06

## Entities

This feature is infrastructure-focused. "Data model" represents configuration entities, not database entities.

### 1. Helm Values Configuration

The primary configuration entity that differs between environments.

**Base (values.yaml)** - shared defaults:
```
backend.image.repository, tag, pullPolicy
backend.replicas, port, resources
frontend.image.repository, tag, pullPolicy
frontend.replicas, port, resources
recurringTask.image.repository, tag, pullPolicy
recurringTask.replicas, port
realtimeSync.image.repository, tag, pullPolicy
realtimeSync.replicas, port
reminder.image.repository, tag, pullPolicy
reminder.replicas, port
audit.image.repository, tag, pullPolicy
audit.replicas, port
dapr.enabled (boolean)
config.logLevel, environment
```

**Local Override (values-local.yaml)** - Minikube-specific:
```
*.image.pullPolicy: IfNotPresent (local images)
*.replicas: 1
dapr.pubsub.brokers: redpanda.redpanda.svc.cluster.local:9093
dapr.statestore.redisHost: redis.redis.svc.cluster.local:6379
config.environment: development
```

**Cloud Override (values-cloud.yaml)** - DOKS/GKE/AKS-specific:
```
*.image.repository: ghcr.io/<org>/<service>
*.image.pullPolicy: Always
*.replicas: 2 (minimum)
dapr.pubsub.brokers: <redpanda-cloud-bootstrap-url>
dapr.pubsub.authRequired: true
dapr.pubsub.saslUsername: (from K8s secret)
dapr.pubsub.saslPassword: (from K8s secret)
config.environment: production
```

### 2. Dapr Component Configuration

| Component | Type | Local Endpoint | Cloud Endpoint |
|-----------|------|---------------|----------------|
| pubsub-redpanda | pubsub.kafka | redpanda.redpanda.svc.cluster.local:9093 | Redpanda Cloud bootstrap URL |
| statestore-redis | state.redis | redis.redis.svc.cluster.local:6379 | Managed Redis or in-cluster Redis |
| cron-reminder | bindings.cron | @every 1m | @every 1m |
| secrets-local | secretstores.local.file | Local file | N/A (use K8s secrets) |

### 3. Kubernetes Secrets

| Secret Name | Keys | Source (Local) | Source (Cloud) |
|-------------|------|----------------|----------------|
| todo-secrets | database-url | Manual / helm --set | GitHub Actions → kubectl |
| todo-secrets | jwt-secret | Manual / helm --set | GitHub Actions → kubectl |
| todo-secrets | cohere-api-key | Manual / helm --set | GitHub Actions → kubectl |
| redpanda-auth | sasl-username | N/A (no auth local) | GitHub Actions → kubectl |
| redpanda-auth | sasl-password | N/A (no auth local) | GitHub Actions → kubectl |

### 4. Docker Image Registry

| Service | Image Name | Tags |
|---------|-----------|------|
| Backend | ghcr.io/{org}/todo-backend | latest, {commit-sha} |
| Frontend | ghcr.io/{org}/todo-frontend | latest, {commit-sha} |
| Recurring Task | ghcr.io/{org}/recurring-task-service | latest, {commit-sha} |
| Realtime Sync | ghcr.io/{org}/realtime-sync-service | latest, {commit-sha} |
| Reminder | ghcr.io/{org}/reminder-service | latest, {commit-sha} |
| Audit | ghcr.io/{org}/audit-service | latest, {commit-sha} |

### 5. CI/CD Pipeline Stages

```
Trigger: push to main
  │
  ├── Detect Changed Services (paths-filter)
  │
  ├── Build Stage (parallel per changed service)
  │   ├── docker build --tag ghcr.io/{org}/{svc}:{sha}
  │   └── docker tag ... :latest
  │
  ├── Push Stage
  │   └── docker push (all built images)
  │
  └── Deploy Stage
      ├── kubectl set image ... (rolling update)
      └── kubectl rollout status (wait for healthy)
```

## Relationships

```
GitHub Actions ──builds──> Docker Images ──pushed to──> GHCR
                                                          │
Helm Chart ──references──> Docker Images                  │
    │                                                     │
    ├── values-local.yaml ──> Minikube Cluster            │
    └── values-cloud.yaml ──> DOKS Cluster ◄──pulls──────┘
                                  │
                              Dapr Components
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
              pubsub-redpanda  statestore   cron-binding
                    │          -redis
                    │
              ┌─────┴──────┐
              │            │
         Local Redpanda  Redpanda Cloud
         (in-cluster)    (Serverless)
```
