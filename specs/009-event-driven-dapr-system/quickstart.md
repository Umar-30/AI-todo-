# Quickstart: Event-Driven Dapr System

**Feature**: 009-event-driven-dapr-system
**Prerequisites**: Minikube, Helm, kubectl, Docker

## 1. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

## 2. Install Dapr

```bash
# Install Dapr CLI (if not already installed)
# Windows: winget install Dapr.CLI
# macOS: brew install dapr/tap/dapr-cli
# Linux: wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init -k --wait

# Verify Dapr is running
dapr status -k
```

Expected output:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
dapr-sidecar-injector  dapr-system  True     Running  1         1.12.x   1m
dapr-operator          dapr-system  True     Running  1         1.12.x   1m
dapr-placement-server  dapr-system  True     Running  1         1.12.x   1m
dapr-sentry            dapr-system  True     Running  1         1.12.x   1m
```

## 3. Deploy Redpanda

```bash
# Add Redpanda Helm repository
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Create namespace
kubectl create namespace redpanda

# Install Redpanda (single-node for development)
helm install redpanda redpanda/redpanda \
  --namespace redpanda \
  --set statefulset.replicas=1 \
  --set resources.memory.container.max=512Mi \
  --set storage.persistentVolume.size=2Gi \
  --set external.enabled=false \
  --wait

# Verify Redpanda is running
kubectl get pods -n redpanda
```

## 4. Deploy Redis

```bash
# Create namespace
kubectl create namespace redis

# Deploy Redis (simple single-node)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: redis
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
EOF

# Verify Redis is running
kubectl get pods -n redis
```

## 5. Apply Dapr Components

```bash
# Apply from the contracts directory
kubectl apply -f specs/009-event-driven-dapr-system/contracts/dapr-components.yaml

# Verify components are registered
dapr components -k
```

Expected output:
```
NAMESPACE  NAME              TYPE                VERSION  SCOPES
default    pubsub-redpanda   pubsub.kafka        v1
default    statestore-redis  state.redis         v1
default    cron-reminder     bindings.cron       v1       reminder-service
default    secrets-local     secretstores.local  v1
```

## 6. Create Kafka Topics

```bash
# Exec into Redpanda pod to create topics
kubectl exec -it redpanda-0 -n redpanda -- rpk topic create task-events --partitions 3
kubectl exec -it redpanda-0 -n redpanda -- rpk topic create reminders --partitions 1
kubectl exec -it redpanda-0 -n redpanda -- rpk topic create task-updates --partitions 3

# Verify topics
kubectl exec -it redpanda-0 -n redpanda -- rpk topic list
```

## 7. Deploy Backend with Dapr Sidecar

```bash
# Build and load backend image
docker build -t todo-backend:dapr -f backend/Dockerfile backend/
minikube image load todo-backend:dapr

# Deploy with Dapr annotations
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: backend
        image: todo-backend:dapr
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: database-url
        - name: DAPR_HTTP_PORT
          value: "3500"
EOF
```

## 8. Test Event Publishing

```bash
# Port-forward to backend
kubectl port-forward svc/todo-backend-svc 8000:8000 &

# Create a task (should publish event)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "user_id": "user-123"}'

# Check Redpanda for the event
kubectl exec -it redpanda-0 -n redpanda -- rpk topic consume task-events --num 1
```

## 9. View Dapr Dashboard

```bash
# Start Dapr dashboard
dapr dashboard -k

# Open http://localhost:8080 in browser
```

## Troubleshooting

### Dapr sidecar not injecting

```bash
# Check namespace has Dapr enabled
kubectl label namespace default dapr-enabled=true

# Check pod annotations
kubectl get pod <pod-name> -o yaml | grep dapr
```

### Events not publishing

```bash
# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd

# Check component status
dapr components -k
```

### Redpanda connection issues

```bash
# Test connectivity from a pod
kubectl run test-kafka --rm -it --image=redpandadata/redpanda:latest -- \
  rpk cluster info --brokers redpanda.redpanda.svc.cluster.local:9093
```

## Next Steps

1. Deploy microservices (recurring-task, reminder, audit, realtime-sync)
2. Configure frontend WebSocket connection
3. Run end-to-end tests
4. Set up observability (Zipkin, Prometheus)

## Cleanup

```bash
# Remove Dapr components
kubectl delete -f specs/009-event-driven-dapr-system/contracts/dapr-components.yaml

# Uninstall Redpanda
helm uninstall redpanda -n redpanda
kubectl delete namespace redpanda

# Uninstall Redis
kubectl delete namespace redis

# Uninstall Dapr
dapr uninstall -k
```
