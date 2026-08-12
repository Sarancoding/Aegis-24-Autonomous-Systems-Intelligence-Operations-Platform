# Ingestion Agent Profile

## Role: Ingestion Specialist

**Primary Responsibility:** Event-driven stream processing for financial/system events with >1,000 events/sec throughput.

---

## Core Competencies

### 1. LlamaIndex Workflows
- Build async DAGs for event routing
- Implement custom workflow nodes for classification
- Handle workflow state transitions

### 2. MCP Connectors
- Configure MCP servers for external data sources
- Implement secure authentication flows
- Handle rate limiting and backoff

### 3. Async Processing
- asyncio-based event listeners
- Concurrent webhook handling
- Non-blocking I/O for all operations

### 4. Redis Deduplication
- Sliding window cache for idempotency
- TTL-based expiration (24 hours default)
- Idempotency key generation from event metadata

---

## Input Sources

| Source | Protocol | Volume | Latency Requirement |
|--------|----------|--------|---------------------|
| Webhooks | HTTP POST | 500/sec | <100ms |
| PostgreSQL CDC | Logical Replication | 300/sec | <500ms |
| RSS Feeds | HTTP GET (polling) | 100/min | <1s |
| Sentry Events | HTTP POST | 50/sec | <200ms |
| GitHub Events | Webhook | 50/sec | <200ms |

---

## Processing Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│   Raw       │ --> │  Deduplicate │ --> │  Classify   │ --> │   Route    │
│   Event     │     │  (Redis)     │     │  Severity   │     │   Module   │
└─────────────┘     └──────────────┘     └─────────────┘     └────────────┘
                           │                    │
                           ▼                    ▼
                    [Duplicate? Drop]    [Severity 1-2 → Module 1
                                          Severity 3-5 → Module 2]
```

### Step 1: Event Reception
```python
async def receive_event(raw_event: dict, source: str) -> str:
    """Receive and validate incoming event."""
    # Validate schema
    if not validate_schema(raw_event, source):
        raise ValidationError(f"Invalid schema from {source}")
    
    # Generate idempotency key
    idem_key = generate_idem_key(raw_event, source)
    
    return idem_key
```

### Step 2: Deduplication Check
```python
async def check_dedup(idem_key: str, ttl_seconds: int = 86400) -> bool:
    """Check if event already processed."""
    exists = await redis.set(
        f"idem:{idem_key}",
        "1",
        nx=True,  # Only set if not exists
        ex=ttl_seconds
    )
    return exists is None  # None means it was set (new event)
```

### Step 3: Classification
```python
async def classify_event(event: dict) -> dict:
    """Classify event severity and intent."""
    prompt = f"""Classify this event:
    Source: {event['source']}
    Type: {event['type']}
    Content: {event['content'][:500]}
    
    Output JSON:
    {{
        "severity": 1-5,
        "intent": "financial"|"system"|"security"|"other",
        "requires_action": true/false
    }}"""
    
    classification = await llm.invoke(prompt)
    return parse_classification(classification)
```

### Step 4: Routing
```python
ROUTE_MAP = {
    ("financial", 1): "research_agent",
    ("financial", 2): "research_agent",
    ("financial", 3): "analyst_agent",
    ("financial", 4): "analyst_agent",
    ("financial", 5): "analyst_agent",
    ("system", _): "remediation_agent",
    ("security", _): "security_agent",
}

async def route_event(classification: dict, event: dict):
    """Route event to appropriate agent."""
    key = (classification['intent'], classification['severity'])
    target_agent = ROUTE_MAP.get(key, "observability_agent")
    
    await publish_to_queue(target_agent, event)
    return target_agent
```

---

## Configuration Files

### config/mcp_servers.json
```json
{
  "servers": [
    {
      "name": "financial_times_rss",
      "type": "rss",
      "url": "https://www.ft.com/rss/home",
      "poll_interval_seconds": 60,
      "rate_limit": 10,
      "auth": null
    },
    {
      "name": "github_events",
      "type": "webhook",
      "endpoint": "/webhooks/github",
      "secret_env": "GITHUB_WEBHOOK_SECRET",
      "events": ["push", "pull_request", "issues"]
    },
    {
      "name": "postgres_cdc",
      "type": "cdc",
      "connection_string_env": "DATABASE_URL",
      "tables": ["transactions", "market_data"],
      "slot_name": "aegis24_cdc_slot"
    }
  ]
}
```

---

## Performance Requirements

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Throughput | >1,000 events/sec | <500 events/sec |
| P99 Latency | <500ms | >2s |
| Dedup Accuracy | 100% | <99.9% |
| Error Rate | <0.1% | >1% |
| Uptime | 99.9% | <99% |

---

## Monitoring & Observability

### Metrics to Emit
- `ingestion.events_received.total` (counter)
- `ingestion.events_dropped.duplicate` (counter)
- `ingestion.classification.latency_ms` (histogram)
- `ingestion.routing.destinations` (counter per destination)
- `ingestion.errors.total` (counter)

### Trace Metadata
```python
emit_trace_metadata(
    module_id="ingestion_bus",
    event_id=event_id,
    source=source,
    idem_key=idem_key,
    classification=classification,
    destination=target_agent,
    latency_ms=latency,
    timestamp=datetime.utcnow()
)
```

---

## Testing Requirements

### Unit Tests
- `test_idempotency_key_generation()`
- `test_dedup_cache_ttl()`
- `test_classification_accuracy()`
- `test_routing_logic()`

### Integration Tests
- `test_webhook_end_to_end()`
- `test_cdc_event_processing()`
- `test_redis_failover_handling()`

### Load Tests
- `test_throughput_1000_events_per_sec()`
- `test_latency_under_load()`

---

## Dependencies

```txt
llama-index>=0.10.0
llama-index-workflows>=0.1.0
redis>=5.0.0
asyncio
aiohttp>=3.9.0
psycopg2-binary>=2.9.0  # For CDC
```

---

## Security Considerations

1. **Webhook Validation:** Always verify HMAC signatures.
2. **Rate Limiting:** Implement per-source rate limits.
3. **PII Scanning:** Scan all ingress for PII before processing.
4. **Credential Management:** Never log secrets, use env vars.

---

*Version: 1.0.0*
*Last Updated: $(date)*
