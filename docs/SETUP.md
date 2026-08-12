# Aegis-24 Setup Guide

## Environment Configuration

### 1. Environment Variables

Copy the example environment file:

```bash
cp harness/.env.example .env
```

Edit `.env` with your configuration:

```ini
# LLM Configuration
OPENAI_API_KEY=sk-your-api-key-here

# Guardrails Configuration
GUARDRAILS_CONFIG=config/guardrails_policy.json

# Observability (Optional)
PHOENIX_ENDPOINT=http://localhost:6006
LANGSMITH_API_KEY=lsv2_your-api-key-here
LANGSMITH_PROJECT=aegis-24

# E2B Sandbox (Optional)
E2B_API_KEY=e2b_your-api-key-here

# Database (Optional)
DATABASE_URL=postgresql://user:pass@localhost:5432/aegis24

# Redis (Optional, for deduplication)
REDIS_URL=redis://localhost:6379

# Slack Webhook (Optional, for alerts)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 2. Guardrails Policy

The guardrails policy is configured in `config/guardrails_policy.json`:

```json
{
  "policy_version": "1.0.0",
  "guardrails": {
    "input_guardrail": {
      "enabled": true,
      "block_prompt_injection": true
    },
    "output_guardrail": {
      "enabled": true,
      "redact_pii": true,
      "enforce_financial_disclaimers": true
    }
  },
  "escalation": {
    "confidence_threshold": 0.8
  }
}
```

### 3. Agent Configuration

Configure agents in `config/agents.yaml`:

```yaml
agents:
  ingestion_agent:
    max_throughput: 1000
    timeout_seconds: 30
  
  research_agent:
    max_iterations: 3
    score_threshold: 0.8
  
  security_agent:
    confidence_threshold: 0.8
```

### 4. MCP Servers

Configure external data sources in `config/mcp_servers.json`:

```json
{
  "mcp_servers": {
    "sec_edgar": {
      "url": "https://www.sec.gov/cgi-bin/browse-edgar",
      "rate_limit": 10
    },
    "github_api": {
      "url": "https://api.github.com",
      "auth_type": "bearer_token"
    }
  }
}
```

## Arize Phoenix Setup

### Local Phoenix Server

```bash
pip install arize-phoenix
phoenix serve
```

Configure in `.env`:
```
PHOENIX_ENDPOINT=http://localhost:6006
```

### LangSmith Setup

1. Create account at https://smith.langchain.com
2. Generate API key
3. Configure in `.env`:
```
LANGSMITH_API_KEY=lsv2_your-key
LANGSMITH_PROJECT=aegis-24
```

## Docker Deployment (Optional)

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache
- Aegis-24 application

## Verification

Run verification script:

```bash
python scripts/setup_phoenix.py
```

Expected output:
```
Phoenix endpoint configured: http://localhost:6006
Tracing enabled: True
```

## Next Steps

1. Run tests: `pytest tests/ -v`
2. Run red team: `make run-redteam`
3. Generate audit report: `make generate-audit`
