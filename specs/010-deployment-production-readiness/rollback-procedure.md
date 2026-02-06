# Rollback Procedure

**Feature**: 010-deployment-production-readiness

## Helm Rollback

### View Release History
```bash
helm history todo-chatbot
```

### Rollback to Previous Version
```bash
helm rollback todo-chatbot 0 --wait --timeout 300s
```
- `0` rolls back to the immediately previous release
- Use a specific revision number to target an exact version

### Rollback to Specific Revision
```bash
helm rollback todo-chatbot <REVISION_NUMBER> --wait --timeout 300s
```

### Verify Rollback
```bash
# Check all pods are running
kubectl get pods

# Verify rollout status for each deployment
kubectl rollout status deployment/todo-backend --timeout=120s
kubectl rollout status deployment/todo-frontend --timeout=120s
kubectl rollout status deployment/recurring-task-service --timeout=120s
kubectl rollout status deployment/realtime-sync-service --timeout=120s
kubectl rollout status deployment/reminder-service --timeout=120s
kubectl rollout status deployment/audit-service --timeout=120s

# Check logs for errors
kubectl logs -l app=todo-backend --tail=20
```

## CI/CD Auto-Rollback

The GitHub Actions pipeline includes automatic rollback on deploy failure:

```yaml
- name: Rollback on failure
  if: failure()
  run: helm rollback todo-chatbot 0 --wait --timeout 300s
```

## Manual Emergency Rollback

If Helm rollback fails, manually set image tags:

```bash
kubectl set image deployment/todo-backend backend=<PREVIOUS_IMAGE>:<TAG>
kubectl set image deployment/todo-frontend frontend=<PREVIOUS_IMAGE>:<TAG>
```

## Post-Rollback Checklist

1. Verify all pods are Running with 2/2 containers (app + Dapr sidecar)
2. Check `/health` endpoints return 200
3. Test frontend loads correctly
4. Verify task CRUD operations work
5. Check Dapr dashboard for healthy components
6. Review logs for any remaining errors
