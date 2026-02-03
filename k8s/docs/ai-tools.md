# AI-Assisted DevOps Tools Guide

This guide documents how to use AI-assisted DevOps tools for the Todo Chatbot Kubernetes deployment, along with standard CLI fallbacks for each operation.

## Overview

| Tool | Purpose | Availability |
|------|---------|--------------|
| Docker AI (Gordon) | Dockerfile generation, builds, explanations | Docker Desktop 4.x+ |
| kubectl-ai | Kubernetes deployment, scaling, debugging | kubectl plugin |
| Kagent | Cluster health analysis, optimization | Standalone tool |

---

## Docker AI (Gordon)

Docker AI (Gordon) is built into Docker Desktop and helps with container-related tasks.

### Usage Examples

#### Generate a Dockerfile

```bash
# AI Command
docker ai "Create a multi-stage Dockerfile for a Python FastAPI application"

# CLI Fallback
# Manually create Dockerfile based on templates in k8s/docker/
```

#### Explain an Existing Dockerfile

```bash
# AI Command
docker ai "Explain the Dockerfile at k8s/docker/backend.Dockerfile"

# CLI Fallback
cat k8s/docker/backend.Dockerfile
# Read comments and Docker documentation
```

#### Optimize Image Size

```bash
# AI Command
docker ai "How can I reduce the size of this Docker image?"

# CLI Fallback
# Use multi-stage builds
# Use slim/alpine base images
# Remove unnecessary files
docker images todo-backend:latest --format "Size: {{.Size}}"
```

#### Debug Build Failures

```bash
# AI Command
docker ai "Why is my Docker build failing with this error: [error message]"

# CLI Fallback
docker build --progress=plain -f k8s/docker/backend.Dockerfile .
docker build --no-cache -f k8s/docker/backend.Dockerfile .
```

#### Build with Gordon

```bash
# AI Command
docker ai "Build the backend Dockerfile and tag it as todo-backend:v1.0"

# CLI Fallback
docker build -t todo-backend:v1.0 -f k8s/docker/backend.Dockerfile .
```

---

## kubectl-ai

kubectl-ai is a kubectl plugin that translates natural language into kubectl commands.

### Installation

```bash
# Install via krew (kubectl plugin manager)
kubectl krew install ai

# Verify installation
kubectl ai --help
```

### Usage Examples

#### Deploy Resources

```bash
# AI Command
kubectl-ai "Deploy the todo-chatbot using the manifests in k8s/manifests/"

# CLI Fallback
kubectl apply -f k8s/manifests/
```

#### Check Pod Status

```bash
# AI Command
kubectl-ai "Show me the status of all todo-chatbot pods"

# CLI Fallback
kubectl get pods -l app.kubernetes.io/name=todo-chatbot
kubectl get pods -l app=todo-backend
kubectl get pods -l app=todo-frontend
```

#### Scale Deployment

```bash
# AI Command
kubectl-ai "Scale the backend deployment to 3 replicas"

# CLI Fallback
kubectl scale deployment todo-backend --replicas=3
```

#### View Logs

```bash
# AI Command
kubectl-ai "Show me the last 50 lines of backend logs"

# CLI Fallback
kubectl logs -l app=todo-backend --tail=50
kubectl logs -l app=todo-backend -f  # Follow logs
```

#### Debug Crashing Pods

```bash
# AI Command
kubectl-ai "Why is my todo-backend pod crashing?"

# CLI Fallback
kubectl describe pod -l app=todo-backend
kubectl logs -l app=todo-backend --previous
kubectl get events --sort-by=.metadata.creationTimestamp
```

#### Port Forward

```bash
# AI Command
kubectl-ai "Forward port 8000 from the backend service to my local machine"

# CLI Fallback
kubectl port-forward svc/todo-backend-svc 8000:8000
```

#### Execute Command in Pod

```bash
# AI Command
kubectl-ai "Run a shell inside the backend pod"

# CLI Fallback
kubectl exec -it $(kubectl get pod -l app=todo-backend -o jsonpath='{.items[0].metadata.name}') -- /bin/sh
```

---

## Kagent

Kagent is an AI-powered Kubernetes agent for cluster analysis and optimization.

### Installation

See Kagent project documentation for installation instructions.

### Usage Examples

#### Cluster Health Check

```bash
# AI Command
kagent "Analyze the overall health of my Kubernetes cluster"

# CLI Fallback
kubectl get nodes
kubectl get pods --all-namespaces
kubectl top nodes
kubectl top pods
```

#### Resource Optimization

```bash
# AI Command
kagent "Suggest resource optimizations for the todo-chatbot deployment"

# CLI Fallback
kubectl top pods -l app.kubernetes.io/name=todo-chatbot
kubectl describe deployment todo-backend | grep -A 10 "Resources:"
# Compare actual usage vs requests/limits
```

#### Network Troubleshooting

```bash
# AI Command
kagent "Diagnose network connectivity issues between frontend and backend"

# CLI Fallback
# Test from frontend pod to backend service
kubectl exec -it $(kubectl get pod -l app=todo-frontend -o jsonpath='{.items[0].metadata.name}') -- wget -q -O- http://todo-backend-svc:8000/health

# Check service endpoints
kubectl get endpoints todo-backend-svc
```

#### Security Analysis

```bash
# AI Command
kagent "Check for security issues in my todo-chatbot deployment"

# CLI Fallback
kubectl auth can-i --list
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].securityContext}'
```

---

## CLI Fallback Reference

All operations must work without AI tools. Here's a complete reference:

### Docker Operations

```bash
# Build images
docker build -t todo-backend:latest -f k8s/docker/backend.Dockerfile .
docker build -t todo-frontend:latest -f k8s/docker/frontend.Dockerfile .

# List images
docker images | grep todo

# Run locally
docker run -p 8000:8000 todo-backend:latest
docker run -p 3000:3000 todo-frontend:latest

# Push to registry (if using external registry)
docker tag todo-backend:latest registry/todo-backend:latest
docker push registry/todo-backend:latest
```

### Kubernetes Operations

```bash
# Apply manifests
kubectl apply -f k8s/manifests/

# Get resources
kubectl get pods,svc,deployments -l app.kubernetes.io/name=todo-chatbot

# Describe resources
kubectl describe deployment todo-backend
kubectl describe pod <pod-name>

# Logs
kubectl logs -l app=todo-backend -f
kubectl logs <pod-name> --previous

# Scale
kubectl scale deployment todo-backend --replicas=3

# Delete
kubectl delete -f k8s/manifests/
```

### Helm Operations

```bash
# Lint
helm lint k8s/helm/todo-chatbot

# Install
helm install todo-chatbot k8s/helm/todo-chatbot

# Upgrade
helm upgrade todo-chatbot k8s/helm/todo-chatbot --set backend.replicas=2

# List releases
helm list

# Uninstall
helm uninstall todo-chatbot

# Rollback
helm rollback todo-chatbot 1
```

### Minikube Operations

```bash
# Start cluster
minikube start --driver=docker --cpus=2 --memory=4096

# Configure Docker
eval $(minikube docker-env)

# Access service
minikube service todo-frontend-svc

# Tunnel for stable access
minikube tunnel

# Dashboard
minikube dashboard

# Stop/Delete
minikube stop
minikube delete
```

---

## Troubleshooting Without AI

See [troubleshooting.md](troubleshooting.md) for common issues and solutions.
