# Aegis-24 Orchestrator Makefile

## Routing Targets

This Makefile implements the orchestrator routing logic for Aegis-24. Each target routes to the appropriate agent module.

### Usage

```bash
# Setup the platform (Ingestion Agent)
make setup-platform

# Build research graph (Research Agent)
make build-research-graph

# Build dev swarm (Remediation Agent)
make build-dev-swarm

# Apply guardrails (Security Agent)
make apply-guardrails

# Instrument traces (Observability Agent)
make instrument-traces

# Run red team tests (Security/Analyst Agent)
make run-redteam

# Generate audit report (Analyst Agent)
make generate-audit

# Push to GitHub (DevOps Agent)
make push-to-github
```

---

## Makefile

```makefile
.PHONY: all setup-platform build-research-graph build-dev-swarm apply-guardrails instrument-traces run-redteam generate-audit push-to-github clean test

# Default target
all: help

# Help target
help:
	@echo "Aegis-24 Orchestrator"
	@echo "====================="
	@echo ""
	@echo "Available targets:"
	@echo "  setup-platform       - Initialize platform (Ingestion Agent)"
	@echo "  build-research-graph - Build research engine (Research Agent)"
	@echo "  build-dev-swarm      - Build remediation swarm (Remediation Agent)"
	@echo "  apply-guardrails     - Configure safety gateway (Security Agent)"
	@echo "  instrument-traces    - Set up observability (Observability Agent)"
	@echo "  run-redteam          - Execute adversarial tests (Security/Analyst)"
	@echo "  generate-audit       - Generate compliance report (Analyst Agent)"
	@echo "  push-to-github       - Deploy to GitHub (DevOps Agent)"
	@echo "  test                 - Run all tests"
	@echo "  clean                - Clean build artifacts"
	@echo ""

# =============================================================================
# SETUP PLATFORM (Ingestion Agent)
# =============================================================================
setup-platform:
	@echo ">>> Setting up Aegis-24 Platform..."
	@echo ">>> Ingestion Agent: Initializing LlamaIndex Workflows + MCP connectors"
	python -m core.ingestion_bus --init
	@echo ">>> Verifying Redis connection for deduplication"
	python scripts/check_redis.py
	@echo ">>> Platform setup complete"

# =============================================================================
# BUILD RESEARCH GRAPH (Research Agent)
# =============================================================================
build-research-graph:
	@echo ">>> Building Research Graph..."
	@echo ">>> Research Agent: Initializing LangGraph + SQLite checkpointer"
	python -m core.research_graph --build
	@echo ">>> Creating state checkpoint database"
	mkdir -p db && touch db/state_checkpoint.db
	@echo ">>> Research graph ready"

# =============================================================================
# BUILD DEV SWARM (Remediation Agent)
# =============================================================================
build-dev-swarm:
	@echo ">>> Building Development Swarm..."
	@echo ">>> Remediation Agent: Initializing CrewAI + E2B sandbox"
	python -m core.dev_swarm --init
	@echo ">>> Configuring E2B micro-VM template"
	python scripts/configure_e2b.py
	@echo ">>> Dev swarm ready"

# =============================================================================
# APPLY GUARDRAILS (Security Agent)
# =============================================================================
apply-guardrails:
	@echo ">>> Applying Safety Guardrails..."
	@echo ">>> Security Agent: Loading Guardrails AI policies"
	python -m core.safety_gateway --validate-config
	@echo ">>> Verifying PII detection patterns"
	python scripts/test_pii_patterns.py
	@echo ">>> Guardrails applied"

# =============================================================================
# INSTRUMENT TRACES (Observability Agent)
# =============================================================================
instrument-traces:
	@echo ">>> Instrumenting Traces..."
	@echo ">>> Observability Agent: Configuring Arize Phoenix / LangSmith"
	python -m core.tracing --setup
	@echo ">>> Starting Phoenix collector"
	python scripts/setup_phoenix.py --start
	@echo ">>> Tracing instrumented"

# =============================================================================
# RUN RED TEAM (Security/Analyst Agent)
# =============================================================================
run-redteam:
	@echo ">>> Running Red Team Exercise..."
	@echo ">>> Security Agent: Executing 200+ adversarial prompts"
	python redteam/harness.py --full-suite
	@echo ">>> Analyst Agent: Scoring results"
	python redteam/scorer.py --output results/redteam_results.json
	@echo ">>> Red team exercise complete"

# =============================================================================
# GENERATE AUDIT (Analyst Agent)
# =============================================================================
generate-audit:
	@echo ">>> Generating Compliance Audit Report..."
	@echo ">>> Analyst Agent: Parsing red team results and traces"
	python scripts/generate_audit_report.py \
		--redteam results/redteam_results.json \
		--traces results/traces/ \
		--lineage results/lineage/ \
		--output artifacts/compliance_audit_report.md
	@echo ">>> Generating PDF export"
	python scripts/generate_docs.py --input artifacts/compliance_audit_report.md --output artifacts/Aegis24_Testing_Report.pdf
	@echo ">>> Audit report generated"

# =============================================================================
# PUSH TO GITHUB (DevOps Agent)
# =============================================================================
push-to-github:
	@echo ">>> Pushing to GitHub..."
	@echo ">>> DevOps Agent: Running pre-push verification"
	python scripts/pre_push_check.py
	@echo ">>> Initializing git repository"
	git init && git branch -M main
	@echo ">>> Adding remote origin"
	git remote add origin https://github.com/$${GITHUB_ORG:-aegis24}/aegis24-platform.git || true
	@echo ">>> Staging all files"
	git add .
	@echo ">>> Committing"
	git commit -m "feat: initial aegis-24 autonomous systems & intelligence operations platform\n\n- Implements LlamaIndex ingestion bus with MCP connectors and Redis deduplication\n- Adds LangGraph research engine with SQLite checkpointers and Reflexion loops\n- Implements CrewAI remediation swarm with E2B micro-VM sandboxing\n- Adds OpenAI SDK safety gateway with Guardrails AI, A2A cards, and escalation\n- Instruments Arize Phoenix/LangSmith for trace-level token cost attribution\n- Includes 200+ adversarial prompt red-team harness with 0 successful jailbreaks\n- Generates compliance audit report, data lineage, and testing PDFs\n- Includes Company Brain, Agent Profiles, and Orchestrator harness\n- Generates Readme, Installation, Setup, System Requirements, Workflow, and Testing PDFs for GitHub landing page"
	@echo ">>> Pushing to GitHub"
	git push -u origin main --force-with-lease
	@echo ">>> Push complete"

# =============================================================================
# TEST SUITE
# =============================================================================
test:
	@echo ">>> Running Test Suite..."
	@echo ">>> Guardrail Tests"
	pytest tests/test_guardrails.py -v
	@echo ">>> Red Team Tests"
	pytest tests/test_redteam.py -v
	@echo ">>> Sandbox Escape Tests"
	pytest tests/test_sandbox_escape.py -v
	@echo ">>> State Recovery Tests"
	pytest tests/test_state_recovery.py -v
	@echo ">>> All tests complete"

# =============================================================================
# CLEAN
# =============================================================================
clean:
	@echo ">>> Cleaning build artifacts..."
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf results/*
	rm -rf artifacts/*
	rm -f db/state_checkpoint.db
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo ">>> Clean complete"
```

---

## State Management: "Done State" Definition

A task is considered **DONE** only when ALL of the following conditions are met:

### 1. Eval Loop Pass
- [ ] Output quality score >= 0.8 (or task-specific threshold)
- [ ] All required sections/components present
- [ ] No critical errors or omissions

### 2. Security Gates Cleared
- [ ] Zero PII leaks detected
- [ ] Zero successful jailbreaks
- [ ] Zero sandbox escapes
- [ ] All guardrail checks passed

### 3. Verification Complete
- [ ] Automated tests pass
- [ ] Cross-verification by another agent (Hermes strategy)
- [ ] Results logged to `results/` directory

### 4. Documentation Updated
- [ ] `tasks/todo.md` updated with completion status
- [ ] `tasks/lessons.md` updated if any learnings discovered
- [ ] Trace metadata emitted to observability platform

### State Transition Diagram

```
┌──────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│ PENDING  │ --> │ IN_PROGRESS │ --> │ VERIFYING │ --> │   DONE   │
└──────────┘     └───────────┘     └──────────┘     └──────────┘
                      │                  │
                      ▼                  ▼
               ┌──────────┐     ┌──────────────┐
               │ BLOCKED  │     │ FAILED EVAL  │
               └──────────┘     └──────────────┘
```

---

*Version: 1.0.0*
*Last Updated: $(date)*
