# Quickstart: Deployment & Production Readiness

**Feature**: 010-deployment-production-readiness
**Date**: 2026-02-06

## Prerequisites

### Tools Required (All Environments)
- Docker Desktop (with Kubernetes support)
- Helm v3.x
- kubectl
- Dapr CLI v1.13+
- Git

### Additional for Local
- Minikube v1.32+

### Additional for Cloud
- `doctl` CLI (DigitalOcean) OR `gcloud` (GKE) OR `az` (AKS)
- GitHub account with Actions enabled
- Redpanda Cloud account

### Additional for CI/CD
- GitHub repository with Actions enabled
- GitHub Container Registry (GHCR) access

## Local Deployment (Minikube)

### Step 1: Start Minikube
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

### Step 2: Install Dapr on Kubernetes
```bash
dapr init -k --wait
dapr status -k  # Verify all components running
```

### Step 3: Deploy Infrastructure
```bash
# Deploy Redpanda (Kafka-compatible broker)
kubectl apply -f k8s/manifests/redpanda/

# Deploy Redis (Dapr state store)
kubectl apply -f k8s/manifests/redis/

# Apply Dapr components
kubectl apply -f dapr/components/
```

### Step 4: Build Local Images
```bash
eval $(minikube docker-env)  # Use Minikube's Docker daemon

# Build all service images
docker build -t todo-backend:latest ./backend/
docker build -t todo-frontend:latest ./AI-todo-new/
docker build -t recurring-task-service:latest ./services/recurring-task-service/
docker build -t realtime-sync-service:latest ./services/realtime-sync-service/
docker build -t reminder-service:latest ./services/reminder-service/
docker build -t audit-service:latest ./services/audit-service/
```

### Step 5: Deploy with Helm
```bash
helm upgrade --install todo-chatbot k8s/helm/todo-chatbot/ \
  -f k8s/helm/todo-chatbot/values-local.yaml \
  --set secrets.create=true \
  --set secrets.databaseUrl="<YOUR_NEON_DATABASE_URL>" \
  --set secrets.jwtSecret="<YOUR_JWT_SECRET>"
```

### Step 6: Verify
```bash
kubectl get pods  # All pods Running
dapr dashboard    # Open Dapr dashboard
minikube service todo-frontend-svc  # Open frontend
```

## Cloud Deployment (DOKS)

### Step 1: Create Cluster
```bash
doctl kubernetes cluster create todo-chatbot \
  --region nyc1 --size s-2vcpu-4gb --count 3
```

### Step 2: Install Dapr
```bash
dapr init -k --wait
```

### Step 3: Create Secrets
```bash
kubectl create secret generic todo-secrets \
  --from-literal=database-url="<NEON_URL>" \
  --from-literal=jwt-secret="<JWT_SECRET>" \
  --from-literal=cohere-api-key="<COHERE_KEY>"

kubectl create secret generic redpanda-auth \
  --from-literal=sasl-username="<REDPANDA_USER>" \
  --from-literal=sasl-password="<REDPANDA_PASS>"
```

### Step 4: Deploy with Helm
```bash
helm upgrade --install todo-chatbot k8s/helm/todo-chatbot/ \
  -f k8s/helm/todo-chatbot/values-cloud.yaml
```

### Step 5: Verify
```bash
kubectl get pods
kubectl logs -l app=todo-backend --tail=20
```

## CI/CD Setup

### Step 1: Configure GitHub Secrets
In your GitHub repo settings, add these secrets:
- `KUBE_CONFIG` - base64-encoded kubeconfig
- `DATABASE_URL` - Neon PostgreSQL connection string
- `JWT_SECRET` - JWT signing secret
- `COHERE_API_KEY` - Cohere API key
- `REDPANDA_SASL_USERNAME` - Redpanda Cloud username
- `REDPANDA_SASL_PASSWORD` - Redpanda Cloud password

### Step 2: Pipeline Triggers Automatically
Push to `main` branch triggers the full build → push → deploy pipeline.

## Smoke Test

After deployment in any environment:

1. **Frontend loads**: Open the application URL
2. **Auth works**: Log in or create an account
3. **Task CRUD**: Create, complete, and delete a task
4. **Recurring**: Create a recurring task, complete it, verify next occurrence
5. **Health checks**: `curl <backend-url>/health` returns 200
6. **Logs visible**: `kubectl logs -l app=todo-backend` shows structured output
