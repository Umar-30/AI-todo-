# Research: Event-Driven Dapr System

**Feature**: 009-event-driven-dapr-system
**Date**: 2026-02-06
**Status**: Complete

## Research Questions

### 1. Dapr Python SDK Patterns for Pub/Sub

**Question**: How to subscribe and publish events using Dapr HTTP API (no direct Kafka clients)?

**Decision**: Use Dapr HTTP API directly with `httpx` or `requests`

**Rationale**:
- Dapr Python SDK provides a client, but HTTP API is simpler and more portable
- Publishing: `POST http://localhost:3500/v1.0/publish/{pubsub-name}/{topic}`
- Subscribing: Register endpoint and configure subscription in component YAML

**Publish Pattern**:
```python
import httpx

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "pubsub-redpanda"

async def publish_event(topic: str, data: dict, metadata: dict = None):
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    headers = {"Content-Type": "application/json"}
    if metadata:
        headers.update({f"metadata.{k}": v for k, v in metadata.items()})
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()
```

**Subscribe Pattern** (declarative):
```yaml
# pubsub-redpanda.yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: pubsub-redpanda
  topic: task-events
  route: /events/task
```

**Alternatives Considered**:
- Dapr Python SDK grpc client: More complex, requires additional dependencies
- Direct Kafka client (kafka-python): REJECTED - violates constraint

---

### 2. Redpanda Deployment on Minikube

**Question**: How to deploy a lightweight Kafka-compatible broker on Minikube?

**Decision**: Use Redpanda Helm chart with single-node configuration

**Rationale**:
- Redpanda is Kafka-compatible, simpler than full Kafka cluster
- Single-node sufficient for development
- Low resource footprint (256MB-512MB memory)

**Deployment Steps**:
```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Install single-node Redpanda
helm install redpanda redpanda/redpanda \
  --namespace redpanda \
  --create-namespace \
  --set statefulset.replicas=1 \
  --set resources.memory.container.max=512Mi \
  --set storage.persistentVolume.size=2Gi
```

**Dapr Pub/Sub Component**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-redpanda
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda.redpanda.svc.cluster.local:9093"
  - name: consumerGroup
    value: "todo-chatbot"
  - name: authRequired
    value: "false"
```

**Alternatives Considered**:
- Apache Kafka with Strimzi: Heavier, more complex for dev
- In-memory Pub/Sub: No persistence, not production-representative

---

### 3. WebSocket + Dapr Integration

**Question**: How to bridge Dapr Pub/Sub events to WebSocket clients?

**Decision**: Service subscribes to Dapr events and maintains WebSocket connection pool

**Rationale**:
- Dapr does not natively support WebSocket push
- Service acts as bridge: Dapr subscription → WebSocket broadcast
- FastAPI supports WebSocket natively

**Architecture**:
```
Dapr Sidecar → POST /events/sync → Realtime Service → WebSocket Manager → Clients
```

**Implementation Pattern**:
```python
from fastapi import FastAPI, WebSocket
from typing import Dict, Set
import asyncio

app = FastAPI()
connections: Dict[str, Set[WebSocket]] = {}  # user_id -> websockets

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    if user_id not in connections:
        connections[user_id] = set()
    connections[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep alive
    finally:
        connections[user_id].discard(websocket)

@app.post("/events/sync")
async def handle_sync_event(event: dict):
    user_id = event.get("userId")
    if user_id in connections:
        message = json.dumps(event)
        for ws in connections[user_id].copy():
            try:
                await ws.send_text(message)
            except:
                connections[user_id].discard(ws)
    return {"status": "ok"}
```

**Alternatives Considered**:
- Server-Sent Events (SSE): Already implemented, but unidirectional
- Polling: Inefficient, high latency

---

### 4. Cron Binding for Scheduled Tasks

**Question**: How to trigger scheduled reminder checks with Dapr?

**Decision**: Use Dapr Cron input binding

**Rationale**:
- Built-in Dapr feature, no external scheduler needed
- Triggers HTTP POST to configured route on schedule
- Simple YAML configuration

**Component Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cron-reminder
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 1m"
  - name: route
    value: /reminders/check
```

**Handler Pattern**:
```python
@app.post("/reminders/check")
async def check_reminders():
    # Query state store for reminders due now
    # Publish reminder.triggered events for each
    pass
```

**Alternatives Considered**:
- APScheduler (Python): Works but external to Dapr ecosystem
- Kubernetes CronJob: Separate deployment, more complexity

---

### 5. Event Schema Versioning

**Question**: How to handle evolving event schemas over time?

**Decision**: Include version field in all events, use envelope pattern

**Rationale**:
- Explicit version allows consumers to handle multiple versions
- Envelope separates metadata from payload
- Backward compatibility by supporting old versions

**Event Envelope Pattern**:
```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "todo-backend",
  "id": "uuid",
  "time": "2026-02-06T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "taskId": "uuid",
    "title": "...",
    ...
  }
}
```

**Versioning Strategy**:
1. Add new optional fields (backward compatible)
2. For breaking changes: new event type (e.g., `task.created.v2`)
3. Consumers handle known versions, log/skip unknown

**Alternatives Considered**:
- Schema Registry (Confluent): Overkill for this scale
- No versioning: Risk of breaking changes

---

## Summary of Decisions

| Topic | Decision | Confidence |
|-------|----------|------------|
| Dapr Pub/Sub | HTTP API with httpx | High |
| Message Broker | Redpanda single-node via Helm | High |
| WebSocket Bridge | FastAPI service with connection pool | High |
| Scheduled Tasks | Dapr Cron binding | High |
| Event Versioning | CloudEvents envelope with version | Medium |

## Open Questions (None)

All research questions resolved. Ready for Phase 1 design.
