# Troubleshooting Guide

**Feature**: 010-deployment-production-readiness

## Common Issues

### 1. Pods Stuck in CrashLoopBackOff

**Symptoms**: Pod restarts repeatedly, status shows `CrashLoopBackOff`

**Diagnose**:
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name> -c <container-name> --previous
```

**Common Causes**:
- Missing environment variables (DATABASE_URL, API keys)
- Database connection refused (check DATABASE_URL secret)
- Port conflict (another process on same port)

**Fix**: Check secrets are created correctly:
```bash
kubectl get secrets
kubectl describe secret todo-secrets
```

### 2. Pods Show 1/2 Containers Ready

**Symptoms**: Pod is Running but only 1/2 containers ready (Dapr sidecar not starting)

**Diagnose**:
```bash
kubectl logs <pod-name> -c daprd
dapr status -k
```

**Common Causes**:
- Dapr not installed on cluster
- Dapr components (pubsub, statestore) not applied
- Redpanda/Redis not running

**Fix**:
```bash
dapr init -k --wait
kubectl apply -f dapr/components/
kubectl get pods -n redis
kubectl get pods -n redpanda
```

### 3. ImagePullBackOff (Cloud)

**Symptoms**: Pod can't pull image from GHCR

**Diagnose**:
```bash
kubectl describe pod <pod-name> | grep -A5 Events
```

**Common Causes**:
- GHCR image not pushed yet
- Repository is private, no imagePullSecret configured
- Wrong image tag

**Fix**: Ensure images are pushed and accessible:
```bash
docker pull ghcr.io/<org>/todo-backend:latest
```

### 4. Helm Upgrade Fails

**Symptoms**: `helm upgrade` returns error

**Diagnose**:
```bash
helm history todo-chatbot
helm get values todo-chatbot
```

**Common Causes**:
- Invalid YAML in values file
- Template rendering error
- Resource quota exceeded

**Fix**: Lint and dry-run first:
```bash
helm lint k8s/helm/todo-chatbot/
helm template todo-chatbot k8s/helm/todo-chatbot/ -f k8s/helm/todo-chatbot/values-local.yaml
```

### 5. Dapr Events Not Flowing

**Symptoms**: Tasks created but recurring/audit/reminder services don't react

**Diagnose**:
```bash
# Check Dapr components
dapr components -k

# Check service logs
kubectl logs -l app=recurring-task-service --tail=50
kubectl logs -l app=audit-service --tail=50

# Check Redpanda topics
kubectl exec -n redpanda redpanda-0 -- rpk topic list
```

**Common Causes**:
- Pubsub component not correctly configured
- Redpanda broker not reachable from Dapr
- Service subscription endpoint not responding

**Fix**: Verify Dapr subscriptions:
```bash
curl http://localhost:<dapr-port>/dapr/subscribe
```

### 6. Frontend Can't Reach Backend

**Symptoms**: Frontend loads but API calls fail

**Diagnose**:
```bash
kubectl get svc
kubectl logs -l app=todo-frontend --tail=20
```

**Common Causes**:
- Backend service name mismatch (expected `todo-backend-svc`)
- CORS not configured for the frontend origin
- Backend pod not ready

**Fix**: Verify service connectivity:
```bash
kubectl exec -it <frontend-pod> -- curl http://todo-backend-svc:8000/health
```

### 7. CI/CD Pipeline Fails at Deploy

**Symptoms**: GitHub Actions build succeeds but deploy fails

**Diagnose**: Check Actions logs for the deploy step

**Common Causes**:
- `KUBE_CONFIG` secret expired or invalid
- Cluster unreachable from GitHub Actions runner
- Helm timeout (pods taking too long to start)

**Fix**:
1. Regenerate kubeconfig: `doctl kubernetes cluster kubeconfig show todo-chatbot | base64`
2. Update `KUBE_CONFIG` secret in GitHub
3. Increase timeout in deploy.yml if pods are slow to start

## Useful Commands

```bash
# Overview of all resources
kubectl get all

# Watch pods in real-time
kubectl get pods -w

# Get all events sorted by time
kubectl get events --sort-by='.lastTimestamp'

# Port-forward to a service for local testing
kubectl port-forward svc/todo-backend-svc 8000:8000

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd --tail=50

# Restart a deployment
kubectl rollout restart deployment/<name>
```
