# Troubleshooting Guide

Common issues and solutions for the Todo Chatbot Kubernetes deployment.

---

## Docker Issues

### Image Build Fails

**Symptom**: `docker build` exits with error

**Solutions**:

1. **Check Dockerfile syntax**:
   ```bash
   docker build --progress=plain -f k8s/docker/backend.Dockerfile .
   ```

2. **Clear Docker cache**:
   ```bash
   docker build --no-cache -f k8s/docker/backend.Dockerfile .
   ```

3. **Check disk space**:
   ```bash
   docker system df
   docker system prune -a  # Clean up unused images
   ```

4. **Verify dependencies exist**:
   ```bash
   cat backend/requirements.txt
   cat frontend/package.json
   ```

### Image Too Large

**Symptom**: Image size > 500MB

**Solutions**:

1. Use multi-stage builds (already implemented)
2. Check `.dockerignore` excludes unnecessary files
3. Use slim/alpine base images
4. Remove development dependencies in final stage

---

## Minikube Issues

### Minikube Won't Start

**Symptom**: `minikube start` hangs or fails

**Solutions**:

1. **Check Docker is running**:
   ```bash
   docker info
   ```

2. **Delete and recreate cluster**:
   ```bash
   minikube delete
   minikube start --driver=docker --cpus=2 --memory=4096
   ```

3. **Check resource availability**:
   - Ensure 2+ CPUs and 4GB+ RAM available
   - Close other resource-heavy applications

### Images Not Found in Minikube

**Symptom**: `ImagePullBackOff` or `ErrImageNeverPull`

**Solutions**:

1. **Configure Docker to use Minikube daemon**:
   ```bash
   eval $(minikube docker-env)
   ```

2. **Rebuild images after configuring**:
   ```bash
   docker build -t todo-backend:latest -f k8s/docker/backend.Dockerfile .
   docker build -t todo-frontend:latest -f k8s/docker/frontend.Dockerfile .
   ```

3. **Or load existing images**:
   ```bash
   minikube image load todo-backend:latest
   minikube image load todo-frontend:latest
   ```

4. **Verify images in Minikube**:
   ```bash
   minikube image ls | grep todo
   ```

---

## Kubernetes Issues

### Pods Not Starting

**Symptom**: Pods stuck in `Pending` state

**Solutions**:

1. **Check events**:
   ```bash
   kubectl describe pod <pod-name>
   kubectl get events --sort-by=.metadata.creationTimestamp
   ```

2. **Check resource constraints**:
   ```bash
   kubectl describe nodes | grep -A 5 "Allocated resources"
   ```

3. **Reduce resource requests** in manifests if needed

### Pods Crashing (CrashLoopBackOff)

**Symptom**: Pods restart repeatedly

**Solutions**:

1. **Check logs**:
   ```bash
   kubectl logs <pod-name>
   kubectl logs <pod-name> --previous
   ```

2. **Check health endpoint**:
   ```bash
   kubectl exec -it <pod-name> -- curl localhost:8000/health
   ```

3. **Check environment variables**:
   ```bash
   kubectl exec -it <pod-name> -- env | grep -E "DATABASE|API"
   ```

4. **Increase probe delays** if app needs more startup time:
   ```yaml
   readinessProbe:
     initialDelaySeconds: 30  # Increase from 10
   ```

### Service Not Accessible

**Symptom**: Cannot reach frontend via NodePort

**Solutions**:

1. **Verify service exists**:
   ```bash
   kubectl get svc todo-frontend-svc
   ```

2. **Check endpoints**:
   ```bash
   kubectl get endpoints todo-frontend-svc
   ```
   If empty, pods aren't matching the selector.

3. **Use minikube service**:
   ```bash
   minikube service todo-frontend-svc --url
   ```

4. **Use tunnel for stable access**:
   ```bash
   minikube tunnel
   # Then access http://localhost:30080
   ```

5. **Port forward as fallback**:
   ```bash
   kubectl port-forward svc/todo-frontend-svc 3000:3000
   ```

### Frontend Can't Reach Backend

**Symptom**: API calls fail from frontend

**Solutions**:

1. **Verify backend service**:
   ```bash
   kubectl get svc todo-backend-svc
   kubectl get endpoints todo-backend-svc
   ```

2. **Test connectivity from frontend pod**:
   ```bash
   kubectl exec -it <frontend-pod> -- wget -q -O- http://todo-backend-svc:8000/health
   ```

3. **Check nginx config** in frontend for correct proxy settings

4. **Check backend logs** for errors:
   ```bash
   kubectl logs -l app=todo-backend
   ```

---

## Helm Issues

### Helm Lint Fails

**Symptom**: `helm lint` reports errors

**Solutions**:

1. **Check YAML syntax**:
   ```bash
   helm template k8s/helm/todo-chatbot
   ```

2. **Validate values.yaml**:
   - Ensure all referenced values exist
   - Check indentation (YAML is space-sensitive)

3. **Check template functions**:
   - Verify `_helpers.tpl` defines all used templates

### Helm Install Fails

**Symptom**: `helm install` exits with error

**Solutions**:

1. **Check for existing release**:
   ```bash
   helm list
   helm uninstall todo-chatbot  # If exists
   ```

2. **Dry-run first**:
   ```bash
   helm install todo-chatbot k8s/helm/todo-chatbot --dry-run
   ```

3. **Check rendered templates**:
   ```bash
   helm template todo-chatbot k8s/helm/todo-chatbot
   ```

---

## Database Connection Issues

**Symptom**: Backend can't connect to database

**Solutions**:

1. **Verify DATABASE_URL is set**:
   ```bash
   kubectl exec -it <backend-pod> -- env | grep DATABASE
   ```

2. **Set via Helm**:
   ```bash
   helm upgrade todo-chatbot k8s/helm/todo-chatbot \
     --set config.databaseUrl="postgresql://..."
   ```

3. **Check network access**:
   - Ensure Neon PostgreSQL allows connections from your IP
   - Verify database credentials are correct

---

## Quick Diagnostic Commands

```bash
# Overall status
kubectl get all -l app.kubernetes.io/name=todo-chatbot

# Pod details
kubectl describe pods -l app.kubernetes.io/name=todo-chatbot

# Recent events
kubectl get events --sort-by=.metadata.creationTimestamp | tail -20

# Resource usage
kubectl top pods -l app.kubernetes.io/name=todo-chatbot

# Logs
kubectl logs -l app=todo-backend --tail=100
kubectl logs -l app=todo-frontend --tail=100
```

---

## Getting Help

1. Check this troubleshooting guide
2. Review [ai-tools.md](ai-tools.md) for AI-assisted debugging
3. Use `kubectl describe` and `kubectl logs` for details
4. Check Kubernetes documentation: https://kubernetes.io/docs/
