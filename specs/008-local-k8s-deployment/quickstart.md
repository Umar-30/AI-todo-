# Quickstart: Deploy Todo Chatbot to Local Kubernetes

**Feature**: 008-local-k8s-deployment
**Time Required**: ~15 minutes
**Difficulty**: Beginner-friendly

This guide walks you through deploying the Phase III Todo Chatbot to a local Minikube cluster using Docker, Kubernetes, and Helm.

---

## Prerequisites

Before starting, ensure you have installed:

| Tool | Version | Verify Command |
|------|---------|----------------|
| Docker Desktop | 4.x+ | `docker --version` |
| Minikube | 1.30+ | `minikube version` |
| kubectl | 1.28+ | `kubectl version --client` |
| Helm | 3.x | `helm version` |

**Optional AI Tools** (recommended but not required):
- Docker AI (Gordon) - built into Docker Desktop
- kubectl-ai - `kubectl krew install ai`
- Kagent - see project documentation

---

## Step 1: Start Minikube

```bash
# Start a local Kubernetes cluster
minikube start --driver=docker --cpus=2 --memory=4096

# Verify cluster is running
kubectl cluster-info

# Configure Docker to use Minikube's daemon
# This allows images built locally to be used in Minikube
eval $(minikube docker-env)
```

**Expected Output**:
```
Kubernetes control plane is running at https://192.168.x.x:8443
```

---

## Step 2: Build Container Images

### Option A: Using Docker AI (Gordon) - Recommended

```bash
# Generate and build backend Dockerfile
docker ai "Build a production Dockerfile for the FastAPI backend in backend/"

# Generate and build frontend Dockerfile
docker ai "Build a production Dockerfile for the Vite React frontend in frontend/"
```

### Option B: Using Standard Docker CLI

```bash
# Build backend image
docker build -t todo-backend:latest -f k8s/docker/backend.Dockerfile .

# Build frontend image
docker build -t todo-frontend:latest -f k8s/docker/frontend.Dockerfile .

# Verify images are built
docker images | grep todo
```

**Expected Output**:
```
todo-backend    latest    abc123    5 minutes ago    250MB
todo-frontend   latest    def456    3 minutes ago    50MB
```

---

## Step 3: Deploy with Helm

### Option A: Using kubectl-ai - Recommended

```bash
# Deploy the entire application
kubectl-ai "Install the todo-chatbot helm chart from k8s/helm/todo-chatbot"
```

### Option B: Using Standard Helm CLI

```bash
# Validate the chart first
helm lint ./k8s/helm/todo-chatbot

# Install the chart
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  --set config.databaseUrl="$DATABASE_URL"

# Verify installation
helm list
```

**Expected Output**:
```
NAME            NAMESPACE   REVISION    STATUS      CHART
todo-chatbot    default     1           deployed    todo-chatbot-0.1.0
```

---

## Step 4: Verify Deployment

### Option A: Using Kagent - Recommended

```bash
# Analyze deployment health
kagent "Check the health of my todo-chatbot deployment"
```

### Option B: Using Standard kubectl

```bash
# Check pod status (wait for Running)
kubectl get pods -l app.kubernetes.io/name=todo-chatbot

# Check services
kubectl get services

# View pod logs if needed
kubectl logs -l app=todo-backend --tail=50
kubectl logs -l app=todo-frontend --tail=50
```

**Expected Output**:
```
NAME                             READY   STATUS    RESTARTS   AGE
todo-backend-xxx-yyy             1/1     Running   0          2m
todo-frontend-xxx-yyy            1/1     Running   0          2m
```

---

## Step 5: Access the Application

### Option A: Minikube Service (Opens Browser)

```bash
# Opens the frontend in your default browser
minikube service todo-frontend-svc
```

### Option B: Minikube Tunnel (Stable URL)

```bash
# In a separate terminal (keep running)
minikube tunnel

# Access at http://localhost:30080
```

### Option C: Port Forward (Manual)

```bash
# Forward frontend port
kubectl port-forward svc/todo-frontend-svc 3000:3000

# Access at http://localhost:3000
```

---

## Common Operations

### Scale the Deployment

```bash
# Scale backend to 3 replicas
kubectl scale deployment todo-backend --replicas=3

# OR using Helm
helm upgrade todo-chatbot ./k8s/helm/todo-chatbot \
  --set backend.replicas=3
```

### Update Configuration

```bash
# Update values and upgrade
helm upgrade todo-chatbot ./k8s/helm/todo-chatbot \
  --set frontend.replicas=2 \
  --set backend.resources.limits.memory=1Gi
```

### View Logs

```bash
# Backend logs
kubectl logs -l app=todo-backend -f

# Frontend logs
kubectl logs -l app=todo-frontend -f
```

### Restart Pods

```bash
# Restart backend pods
kubectl rollout restart deployment/todo-backend
```

---

## Cleanup

### Uninstall the Application

```bash
# Remove Helm release
helm uninstall todo-chatbot

# Verify removal
kubectl get all -l app.kubernetes.io/name=todo-chatbot
```

### Stop Minikube

```bash
# Stop the cluster (preserves state)
minikube stop

# OR delete completely
minikube delete
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name>

# Common issues:
# - ImagePullBackOff: Image not found in Minikube
#   Fix: Run `eval $(minikube docker-env)` before building
# - CrashLoopBackOff: Application crashing
#   Fix: Check logs with `kubectl logs <pod-name>`
```

### Cannot Access Frontend

```bash
# Verify service exists
kubectl get svc todo-frontend-svc

# Check NodePort
kubectl get svc todo-frontend-svc -o jsonpath='{.spec.ports[0].nodePort}'

# Try tunnel if NodePort not working
minikube tunnel
```

### Backend Health Check Failing

```bash
# Check if /health endpoint exists
kubectl exec -it <backend-pod> -- curl localhost:8000/health

# If missing, add health endpoint to FastAPI app:
# @app.get("/health")
# def health(): return {"status": "ok"}
```

---

## Next Steps

1. Explore the [plan.md](./plan.md) for architecture details
2. Review [contracts/](./contracts/) for Kubernetes manifest specs
3. Run `/sp.tasks` to see implementation tasks
4. Customize `values.yaml` for your environment
