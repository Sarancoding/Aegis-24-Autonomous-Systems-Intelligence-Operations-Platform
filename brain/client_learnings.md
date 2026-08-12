# Client Learnings Log

## Lessons Learned from Aegis-24 Development & Operations

This document captures hard-won lessons from building and operating autonomous financial systems. Review at session start and update after any incident or correction.

---

## Active Lessons

### 2024-01-15: Reflexion Loop Token Burn Prevention

**Issue:** Initial research graph implementation had no iteration cap, causing runaway token consumption on difficult queries.

**Impact:** Single query consumed $47 in tokens over 23 iterations without achieving quality threshold.

**Resolution:** 
- Hard cap at 3 iterations (per AGENTS.md constraint)
- Warning log at iteration 2
- Automatic escalation to human review if score < 0.8 after 3 iterations

**Rule:** `ALWAYS cap Reflexion loops at 3 iterations to prevent infinite token burn.`

**Verified By:** Token budget enforcement tests in `tests/test_token_budget.py`

---

### 2024-01-14: CDC Event Idempotency

**Issue:** PostgreSQL CDC events were being processed multiple times during failover, causing duplicate research tasks.

**Impact:** 15% duplicate rate in research outputs, wasted token spend, confused audit trail.

**Resolution:**
- Implement idempotency keys based on event LSN + timestamp
- Redis sliding cache for deduplication (TTL: 24 hours)
- Check idempotency before routing to any downstream module

**Rule:** `CDC events require idempotency keys. Check before processing.`

**Verified By:** Deduplication tests in `tests/test_ingestion_dedup.py`

---

### 2024-01-13: PII in Trace Logs

**Issue:** Arize Phoenix traces initially included raw prompt text, which sometimes contained PII from user inputs.

**Impact:** Potential GDPR/CCPA violation - PII stored in observability platform.

**Resolution:**
- Strip PII from trace metadata before emission
- Hash any sensitive fields
- Configure Phoenix to exclude specific attributes from logging

**Rule:** `ALWAYS mask PII in logs and traces. Never send raw PII to observability platforms.`

**Verified By:** PII scanning tests in `tests/test_guardrails.py`

---

### 2024-01-12: Sandbox Timeout Configuration

**Issue:** Default sandbox timeout (60s) was too short for complex pytest suites, causing false failures.

**Impact:** 34% of valid remediation attempts failed due to timeout, not code errors.

**Resolution:**
- Increase default timeout to 300s
- Add progress heartbeat to detect truly hung processes
- Implement graceful termination with partial result capture

**Rule:** `Set sandbox timeout >= 300s for pytest execution. Monitor heartbeats.`

**Verified By:** Sandbox execution tests in `tests/test_sandbox_escape.py`

---

### 2024-01-11: Guardrail Confidence Thresholds

**Issue:** Initial guardrail confidence threshold (0.5) produced too many false positives, blocking legitimate queries.

**Impact:** 23% false positive rate, user frustration, manual review backlog.

**Resolution:**
- Raise threshold to 0.8 for auto-block
- Add 0.7-0.8 "gray zone" for human escalation
- Below 0.7 = auto-allow with monitoring

**Rule:** `Confidence-based escalation: >=0.8 auto-block, 0.7-0.8 escalate, <0.7 allow+monitor.`

**Verified By:** Guardrail performance metrics in audit reports

---

### 2024-01-10: State Checkpoint Corruption

**Issue:** SQLite checkpointer without WAL mode caused database locks during concurrent graph executions.

**Impact:** 12% of graph executions failed with "database locked" error.

**Resolution:**
- Enable WAL mode: `PRAGMA journal_mode=WAL`
- Add connection pooling with timeout
- Implement retry logic for lock conflicts

**Rule:** `ALWAYS enable WAL mode for SQLite checkpointers. Use connection pooling.`

**Verified By:** State recovery tests in `tests/test_state_recovery.py`

---

### 2024-01-09: MCP Connector Rate Limits

**Issue:** MCP server connectors had no rate limiting, causing API bans from external services.

**Impact:** RSS feed and GitHub connectors banned after 500 requests in 1 minute.

**Resolution:**
- Implement token bucket rate limiting per connector
- Add exponential backoff on 429 responses
- Cache responses where appropriate

**Rule:** `Rate limit all external connectors. Respect Retry-After headers.`

**Verified By:** Load tests in `tests/test_ingestion_throughput.py`

---

### 2024-01-08: Financial Disclaimer Placement

**Issue:** Initial reports placed disclaimer in footer, which some parsers missed.

**Impact:** Regulatory risk - reports could be misinterpreted as financial advice.

**Resolution:**
- Move disclaimer to HEADER of all financial content
- Make disclaimer bold and impossible to miss
- Include disclaimer in API response metadata

**Rule:** `ALWAYS place financial disclaimer at the TOP of reports, not the bottom.`

**Verified By:** Compliance scans in `tests/test_guardrails.py`

---

### 2024-01-07: Cross-Context Contamination

**Issue:** Financial data context and system error context were mixed in prompt assembly, causing model confusion.

**Impact:** 8% of outputs included irrelevant system error messages in financial analysis.

**Resolution:**
- Strictly separate context types in prompt templates
- Use different model instances for financial vs. system tasks
- Add context validation before LLM invocation

**Rule:** `NEVER mix financial data context with system error context in prompts.`

**Verified By:** Output quality audits

---

### 2024-01-06: Red Team Harness Timing

**Issue:** Red team harness was run ad-hoc, not before every commit. Some jailbreaks made it to production.

**Impact:** Critical security vulnerability deployed (patched within 2 hours).

**Resolution:**
- Integrate red team harness into CI/CD pipeline
- Block commits if any adversarial prompt succeeds
- Run full 200-prompt suite on every PR

**Rule:** `ALWAYS run red team harness before any commit. Zero tolerance for jailbreaks.`

**Verified By:** CI/CD pipeline configuration

---

## Historical Lessons (Resolved)

### 2024-01-05: E2B API Key Rotation ~~(RESOLVED)~~

**Issue:** Static E2B API key in environment variable for 30+ days.

**Resolution:** Implemented automatic key rotation every 7 days via secrets manager.

**Status:** ✅ Resolved - Automated rotation active.

---

### 2024-01-04: LangGraph Version Compatibility ~~(RESOLVED)~~

**Issue:** LangGraph 0.0.12 broke checkpoint schema compatibility.

**Resolution:** Pinned version to `langgraph==0.0.11` in requirements.txt. Added migration script.

**Status:** ✅ Resolved - Version pinned, migration tested.

---

## Rules Summary (Quick Reference)

1. **ALWAYS** cap Reflexion loops at 3 iterations.
2. **ALWAYS** run red team harness before any commit.
3. **ALWAYS** mask PII in logs and traces.
4. **ALWAYS** place financial disclaimer at report header.
5. **ALWAYS** enable WAL mode for SQLite checkpointers.
6. **ALWAYS** check idempotency for CDC events.
7. **NEVER** mix financial and system error contexts.
8. **NEVER** accept stopgaps - fix root causes.
9. **ALWAYS** rate limit external connectors.
10. **ALWAYS** use confidence-based escalation (0.8/0.7 thresholds).

---

## How to Update This Document

After any incident, correction, or learning:

1. Add new entry under "Active Lessons" with date.
2. Document: Issue, Impact, Resolution, Rule.
3. Add verification test reference.
4. After 30 days without recurrence, move to "Historical Lessons".
5. Update "Rules Summary" if new permanent rule created.

**Review Cadence:** Weekly review in team sync.  
**Owner:** Security/Compliance Lead.

---

*Last Updated: $(date)*
*Version: 1.0.0*
