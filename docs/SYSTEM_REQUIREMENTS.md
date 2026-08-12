# Aegis-24 System Requirements

## Hardware Requirements

### Minimum Configuration

| Component | Requirement |
|-----------|-------------|
| CPU | 4 cores (Intel i5 or equivalent) |
| RAM | 8 GB |
| Storage | 10 GB available space |
| Network | Broadband internet connection |

### Recommended Configuration

| Component | Requirement |
|-----------|-------------|
| CPU | 8 cores (Intel i7 or equivalent) |
| RAM | 16 GB |
| Storage | 20 GB SSD |
| Network | High-speed internet connection |

### Production Configuration

| Component | Requirement |
|-----------|-------------|
| CPU | 16+ cores |
| RAM | 32+ GB |
| Storage | 50+ GB NVMe SSD |
| Network | Low-latency, high-throughput |

## Software Requirements

### Operating System

- **Linux**: Ubuntu 20.04+, Debian 11+, RHEL 8+
- **macOS**: macOS 12+ (Monterey or later)
- **Windows**: Windows 11 with WSL2

### Python Environment

- **Python Version**: 3.10 or higher
- **pip**: Version 22.0 or higher
- **Virtual Environment**: venv or conda recommended

### Required Dependencies

```txt
# Core dependencies (see requirements.txt)
asyncio>=3.4.3
pytest>=7.0.0
pytest-asyncio>=0.21.0
pyyaml>=6.0
```

### Optional Dependencies

| Component | Package | Purpose |
|-----------|---------|---------|
| Arize Phoenix | arize-phoenix | Observability |
| LangSmith | langsmith | Trace tracking |
| E2B SDK | e2b | Sandbox execution |
| Redis | redis-py | Deduplication cache |
| PostgreSQL | psycopg2 | Database storage |

## Docker Requirements (Optional)

If using Docker deployment:

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Container Registry Access**: Docker Hub or GHCR

## Network Requirements

### Firewall Rules

| Port | Protocol | Direction | Purpose |
|------|----------|-----------|---------|
| 443 | HTTPS | Outbound | API calls (OpenAI, SEC, GitHub) |
| 6006 | HTTP | Inbound | Arize Phoenix UI (local) |
| 5432 | TCP | Inbound/Outbound | PostgreSQL (if used) |
| 6379 | TCP | Inbound/Outbound | Redis (if used) |

### API Endpoints

The following external services are accessed:

- `https://api.openai.com` - LLM inference
- `https://www.sec.gov` - Financial filings
- `https://api.github.com` - Code repository access
- `https://api.smith.langchain.com` - LangSmith (optional)

## Browser Requirements (for UI)

If accessing Phoenix/LangSmith dashboards:

- **Chrome**: Version 100+
- **Firefox**: Version 90+
- **Safari**: Version 15+
- **Edge**: Version 100+

## Performance Benchmarks

### Expected Throughput

| Operation | Target | Notes |
|-----------|--------|-------|
| Event Ingestion | >1,000 events/sec | With Redis deduplication |
| Research Query | <30 seconds | 3 iteration max |
| Remediation Task | <10 minutes | Including sandbox testing |
| Security Validation | <1 second | Per input/output |

### Latency Targets

| Component | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| Ingestion | 10ms | 50ms | 100ms |
| Research | 5s | 15s | 30s |
| Security | 100ms | 500ms | 1s |

## Scalability Considerations

### Horizontal Scaling

- **Ingestion Bus**: Can be sharded by event type
- **Research Graph**: Stateless, can run multiple instances
- **Dev Swarm**: Queue-based, scale workers independently
- **Safety Gateway**: Stateless, load-balance easily

### Vertical Scaling

- Increase LLM context window for complex research
- Add more RAM for larger checkpoint databases
- Use faster CPUs for cryptographic operations

## Monitoring Requirements

### Metrics to Track

- Token usage per module
- API call latency
- Guardrail violation count
- Sandbox execution time
- Checkpoint database size

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| PII Leaks | Any | Any |
| Jailbreak Success | Any | Any |
| API Error Rate | >5% | >10% |
| Latency P95 | >2x target | >5x target |
