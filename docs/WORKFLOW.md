# Aegis-24 Workflow Guide

## System Architecture Overview

Aegis-24 is a production-hardened autonomous agent platform with five core components:

```
┌─────────────────────────────────────────────────────────────────┐
│                     AEGIS-24 PLATFORM                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Ingestion│→ │ Research │→ │Remediation│→ │ Security │       │
│  │   Bus    │  │  Graph   │  │  Swarm   │  │ Gateway  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│       ↓             ↓              ↓             ↓              │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              Observability (Tracing)                 │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Component Workflows

### 1. Ingestion DAG (Data Flow)

```
Webhook/CDC Event
       ↓
┌─────────────┐
│ Deduplicate │ ← Redis sliding cache (5 min window)
│  (Redis)    │
└─────────────┘
       ↓
┌─────────────┐
│  Classify   │ ← Severity + Intent classification
│ Severity/   │
│   Intent    │
└─────────────┘
       ↓
┌─────────────┐
│   Route to  │ → security_agent | research_agent |
│   Module    │ → remediation_agent | ingestion_agent
└─────────────┘
```

**Key Features:**
- Async event-driven processing
- Idempotency via Redis deduplication
- >1,000 events/sec throughput target
- MCP connector support for external data sources

### 2. Research State Machine (Cyclic Graph)

```
┌─────────┐     ┌───────────┐     ┌────────┐     ┌────────┐
│ Planner │ →   │ Researcher│ →   │ Writer │ →   │ Critic │
└─────────┘     └───────────┘     └────────┘     └────────┘
     ↑                                              │
     │              Score < 0.8?                    │
     └────────────────── Yes ───────────────────────┘
                      No ↓
                ┌──────────┐
                │   Emit   │
                │  Report  │
                └──────────┘
```

**Key Features:**
- LangGraph-style stateful execution
- SQLite checkpointing at every node
- Reflexion loop capped at 3 iterations
- Quality score threshold: 0.8

**State Persistence:**
```
Every Node → SQLite Checkpoint → Recovery on Restart
```

### 3. Remediation Swarm (Hierarchical Process)

```
┌─────────────────┐
│ Project Manager │ → Define requirements & scope
└────────┬────────┘
         ↓
┌─────────────────┐
│   Architect     │ → Design solution approach
└────────┬────────┘
         ↓
┌─────────────────┐
│   Developer     │ → Implement fix (generate patch)
└────────┬────────┘
         ↓
┌─────────────────┐
│  QA Engineer    │ → Execute pytest in E2B sandbox
└────────┬────────┘
         ↓
    Tests Pass?
    ├─ Yes → Complete
    └─ No  → Retry Dev (max 3 retries)
```

**Key Features:**
- CrewAI hierarchical agent swarm
- E2B micro-VM sandbox isolation
- Zero local code execution
- Automatic retry on test failure

### 4. Safety Gateway (Policy Enforcement Graph)

```
┌─────────────────┐
│ Input Guardrail │ ← Prompt injection detection
└────────┬────────┘
         ↓
┌─────────────────┐
│ Agent Execution │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Output Guardrail│ ← PII redaction, compliance check
└────────┬────────┘
         ↓
    Confidence ≥ 0.8?
    ├─ Yes → Auto-Deploy
    └─ No  → Escalate to Human
```

**Key Features:**
- Guardrails AI policy enforcement
- PII detection and redaction
- SEC/FINRA compliance checking
- Confidence-based escalation

### 5. Data Lineage Flow

```
Raw Files / Source Tables
          ↓
      Staging
          ↓
    Processed
          ↓
     Curated
          ↓
ML Models / Dashboards
```

**Tracking:**
- Every transformation logged
- Source-to-destination traceability
- Timestamp recording
- Module attribution

## Token Management

### Cost Attribution

Every LLM call emits trace metadata:

```python
{
    "module_id": "research_agent",
    "prompt_type": "deep_research",
    "token_count": 2300,
    "cost_usd": 0.046
}
```

### Budget Enforcement

| Constraint | Limit |
|------------|-------|
| Reflexion Loop Iterations | Max 3 |
| Per-Request Token Budget | Configurable |
| Per-Module Daily Budget | Configurable |

## Context Isolation

Financial data context and system error context are strictly separated:

```
┌─────────────────┐    ┌─────────────────┐
│ Financial Data  │    │ System Errors   │
│    Context      │    │    Context      │
└─────────────────┘    └─────────────────┘
         ↓                       ↓
    Separate Processing Pipelines
         ↓                       ↓
    No Cross-Contamination
```

## Eval Loop

```
┌─────────────────────────────────────────┐
│           Generate Output               │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Analyst Agent Judges vs Good Examples  │
└─────────────────┬───────────────────────┘
                  ↓
         ┌────────┴────────┐
         │                 │
    Pass Gate         Fail Gate
         │                 │
         ↓                 ↓
    ✅ Complete      Feed Miss Back
                          ↓
                   Update lessons.md
                          ↓
                    Re-run Agent
```

**Security Gate (Binary):**
- 0 PII leaks allowed
- 0 successful jailbreaks
- 0 sandbox escapes

## Orchestration Commands

```bash
make setup-platform      # Initialize platform
make build-research-graph # Build research engine  
make build-dev-swarm     # Build remediation swarm
make apply-guardrails    # Apply security policies
make instrument-traces   # Set up observability
make run-redteam         # Run adversarial testing
make generate-audit      # Generate compliance report
make push-to-github      # Deploy to GitHub
```

## Done State Criteria

A task is only considered done when:
1. ✅ Eval Loop passes
2. ✅ Security gates cleared
3. ✅ Zero PII leaks
4. ✅ Zero jailbreaks
5. ✅ Sandbox escape prevented
