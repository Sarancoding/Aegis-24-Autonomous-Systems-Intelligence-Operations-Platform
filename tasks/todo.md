# Aegis-24 Task List

## Phase 1: The Company Brain (Knowledge Layer) ✅

### 1.1 Knowledge Base Construction (`brain/`)
- [x] `brain/strategy_docs/financial_compliance.md` - SEC/FINRA constraints
- [x] `brain/strategy_docs/pii_protection.md` - PII categories and redaction protocols
- [x] `brain/sops/sandbox_security.md` - E2B micro-VM isolation SOP
- [x] `brain/sops/graph_orchestration.md` - LangGraph state persistence SOP
- [x] `brain/sops/prompting_techniques.md` - Decision tree for prompting
- [x] `brain/examples/good_audit_report.md` - Example compliance audit report
- [x] `brain/client_learnings.md` - Lessons learned log

### 1.2 Agent Profiles (`agents/`)
- [x] `agents/ingestion_agent.md` - Ingestion Specialist profile
- [x] `agents/research_agent.md` - Research Specialist profile
- [x] `agents/remediation_agent.md` - Remediation Specialist profile
- [x] `agents/security_agent.md` - Security/Compliance Specialist profile
- [x] `agents/observability_agent.md` - Observability Specialist profile
- [x] `agents/analyst_agent.md` - Compliance Analyst profile

---

## Phase 2: The Harness & Orchestrator (System Design) 🔄

### 2.1 The Orchestrator Logic (`orchestrator/`)
- [ ] Create Makefile with routing targets
- [ ] Define state management for "Done State"

### 2.2 Token Management & Context Propagation
- [ ] Implement token tracking metadata
- [ ] Define context isolation rules
- [ ] Implement budget enforcement

### 2.3 The Harness Template (`harness/`)
- [ ] `harness/CLAUDE.md` - Instructions for AI agents
- [ ] `harness/agents.md` - Links to agent profiles
- [ ] `harness/openclawed_loops.md` - CI/CD loop definitions
- [ ] `harness/.env.example` - Environment variables template

### 2.4 Graph Engineering & Loops
- [ ] Design Ingestion DAG
- [ ] Design Research State Machine
- [ ] Design Remediation Swarm
- [ ] Design Safety Gateway
- [ ] Design Eval Loop

---

## Phase 3: Execution & Skills Usage (The Build) ⏳

### 3.1 Core Implementation
- [ ] `core/ingestion_bus.py` - LlamaIndex Workflows + MCP
- [ ] `core/research_graph.py` - LangGraph + SQLite checkpointer
- [ ] `core/dev_swarm.py` - CrewAI + E2B sandbox
- [ ] `core/safety_gateway.py` - Guardrails AI + A2A cards
- [ ] `core/tracing.py` - Arize Phoenix/LangSmith instrumentation

### 3.2 Configuration Files
- [ ] `config/agents.yaml` - Agent configurations
- [ ] `config/tasks.yaml` - Task definitions
- [ ] `config/guardrails_policy.json` - Guardrail policies
- [ ] `config/mcp_servers.json` - MCP server configs

### 3.3 Red Team Harness
- [ ] `redteam/adversarial_prompts.json` - 200+ prompts
- [ ] `redteam/harness.py` - Test execution
- [ ] `redteam/scorer.py` - Result scoring

### 3.4 Scripts
- [ ] `scripts/generate_audit_report.py` - Report generation
- [ ] `scripts/generate_docs.py` - PDF generation from MD
- [ ] `scripts/setup_phoenix.py` - Phoenix setup

### 3.5 Tests
- [ ] `tests/test_guardrails.py` - PII leak tests
- [ ] `tests/test_redteam.py` - Adversarial prompt tests
- [ ] `tests/test_sandbox_escape.py` - Sandbox isolation tests
- [ ] `tests/test_state_recovery.py` - Checkpoint recovery tests

---

## Phase 4: The Eval Loop (Verification) ⏳

### 4.1 Automated Checks
- [ ] `pytest tests/test_guardrails.py` passes with 0 PII leaks
- [ ] `python redteam/harness.py` completes 200 prompts with 0 jailbreaks
- [ ] `tests/test_sandbox_escape.py` fails to escape E2B
- [ ] `tests/test_state_recovery.py` resumes from checkpoint
- [ ] Traces visible in Arize Phoenix/LangSmith

### 4.2 Quality Gate
- [ ] Analyst Agent compares audit report vs. example
- [ ] Red team pass rate = 100%
- [ ] Token costs attributed per trace
- [ ] Guardrail policy documented
- [ ] Data lineage traceable

---

## Phase 5: Artifacts & Landing Page ⏳

### 5.1 Documentation (Markdown)
- [ ] `docs/INSTALLATION.md` - Step-by-step setup
- [ ] `docs/SETUP.md` - Environment configuration
- [ ] `docs/SYSTEM_REQUIREMENTS.md` - Hardware/software requirements
- [ ] `docs/WORKFLOW.md` - System workflow explanation

### 5.2 PDF Generation (MANDATORY)
- [ ] `Aegis24_Readme.pdf` - Generated from README.md
- [ ] `Aegis24_Installation_Guide.pdf` - From docs/INSTALLATION.md
- [ ] `Aegis24_Setup_Guide.pdf` - From docs/SETUP.md
- [ ] `Aegis24_System_Requirements.pdf` - From docs/SYSTEM_REQUIREMENTS.md
- [ ] `Aegis24_Workflow.pdf` - From docs/WORKFLOW.md
- [ ] `Aegis24_Testing_Report.pdf` - From artifacts/compliance_audit_report.md

### 5.3 Repository Files
- [ ] `README.md` - Landing page (must link ALL PDFs)
- [ ] `GITMORE.md` - Dev log & changelog
- [ ] `requirements.txt` - Python dependencies
- [ ] `docker-compose.yml` - Container orchestration
- [ ] `main.py` - Entry point
- [ ] `.gitignore` - Proper exclusions

---

## Phase 6: GitHub Deployment (Mandatory Task) ⏳

### 6.1 Pre-Push Verification
- [ ] `.gitignore` excludes sensitive files
- [ ] `README.md` links to ALL 6 PDFs
- [ ] `GITMORE.md` present with dev log
- [ ] All 6 PDFs generated and in repo root
- [ ] All tests pass with 0 critical failures
- [ ] No hardcoded API keys or secrets
- [ ] Red team harness shows 200/200 blocked
- [ ] Data lineage traceable

### 6.2 Git Operations
- [ ] Initialize git repo
- [ ] Add remote origin
- [ ] Commit all files
- [ ] Push to GitHub

### 6.3 Post-Push Verification
- [ ] Repo URL accessible
- [ ] README.md renders correctly
- [ ] All 6 PDFs linked and downloadable
- [ ] GITMORE.md visible
- [ ] Mark "Push to GitHub" as DONE

---

## Current Status

**Phase:** 1 ✅ COMPLETE  
**Next Action:** Continue Phase 2 - Harness & Orchestrator design

---

*Last Updated: $(date)*
