# Phase IV: Local Kubernetes Deployment

Deploy the Todo Chatbot to a local Minikube cluster using Docker, Kubernetes, and Helm.

## Prerequisites

Before starting, ensure you have installed:

| Tool | Version | Verify Command | Install Guide |
|------|---------|----------------|---------------|
| Docker Desktop | 4.x+ | `docker --version` | https://docs.docker.com/desktop/ |
| Minikube | 1.30+ | `minikube version` | https://minikube.sigs.k8s.io/docs/start/ |
| kubectl | 1.28+ | `kubectl version --client` | https://kubernetes.io/docs/tasks/tools/ |
| Helm | 3.x | `helm version` | https://helm.sh/docs/intro/install/ |

### Optional AI Tools

| Tool | Purpose | Install |
|------|---------|---------|
| Docker AI (Gordon) | Dockerfile generation | Built into Docker Desktop 4.x+ |
| kubectl-ai | K8s deployment assistance | `kubectl krew install ai` |
| Kagent | Cluster health analysis | See project docs |

## Quick Start

```bash
# 1. Start Minikube
minikube start --driver=docker --cpus=2 --memory=4096

# 2. Configure Docker to use Minikube's daemon
eval $(minikube docker-env)

# 3. Build images
docker build -t todo-backend:latest -f k8s/docker/backend.Dockerfile .
docker build -t todo-frontend:latest -f k8s/docker/frontend.Dockerfile .

# 4. Deploy with Helm
helm install todo-chatbot ./k8s/helm/todo-chatbot

# 5. Access the application
minikube service todo-frontend-svc
```

## Directory Structure

```
k8s/
├── docker/
│   ├── backend.Dockerfile    # FastAPI backend image
│   ├── frontend.Dockerfile   # React/Nginx frontend image
│   ├── nginx.conf            # Nginx configuration
│   └── .dockerignore
├── manifests/
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   └── configmap.yaml
├── helm/
│   └── todo-chatbot/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
└── docs/
    ├── ai-tools.md
    └── troubleshooting.md
```

## Deployment Options

### Option 1: Raw Kubernetes Manifests

```bash
kubectl apply -f k8s/manifests/
```

### Option 2: Helm Chart (Recommended)

```bash
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  --set config.databaseUrl="$DATABASE_URL"
```

## Common Commands

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=todo-chatbot

# View logs
kubectl logs -l app=todo-backend -f

# Scale deployment
kubectl scale deployment todo-backend --replicas=3

# Uninstall
helm uninstall todo-chatbot
```

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for common issues and solutions.
