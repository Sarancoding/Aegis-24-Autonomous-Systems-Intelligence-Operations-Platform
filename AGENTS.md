# AGENTS.md - System Constraints & Operating Principles

## Core Philosophy
This document defines the operating principles for all AI agents working on this codebase. These rules are non-negotiable and must be followed in every interaction.

## 1. Implementation Rules

### 1.1 No Backward Compatibility
- **Do not preserve backward compatibility.** Remove obsolete paths, deprecated functions, and legacy code immediately.
- When refactoring, delete the old implementation before adding the new one.
- Version migration is the user's responsibility, not the codebase's burden.

### 1.2 Simplest Implementation
- **Choose the simplest implementation** that satisfies requirements.
- Avoid over-engineering. Prefer readability over cleverness.
- If a standard library function exists, use it instead of a custom solution.
- Complexity must be justified by measurable performance or security gains.

### 1.3 Modular Design
- **Keep components modular and concerns clearly separated.**
- Each module should have a single responsibility.
- Use clear interfaces between components.
- Avoid circular dependencies.

### 1.4 Dependency Discipline
- **Prefer established, well-maintained libraries.**
- Check library maintenance status, issue tracker activity, and release frequency before adding.
- **Lean on dependencies already in the project** before introducing new ones.
- Pin all dependency versions in `requirements.txt`.

### 1.5 Long-Term Architecture
- **Make architectural decisions for the long term.** Do not accept stopgaps.
- Every commit should move the system toward production readiness.
- Technical debt must be documented in `tasks/lessons.md` with a remediation plan.

## 2. Security & Privacy

### 2.1 PII Protection
- All PII must be masked/redacted at ingress and egress points.
- Never log sensitive data (API keys, passwords, tokens, SSNs, account numbers).
- Use environment variables for secrets; never hardcode credentials.

### 2.2 Sandboxed Execution
- All code execution must occur within E2B micro-VMs or equivalent isolation.
- Zero local execution escaping is permitted.
- Validate all inputs before passing to sandboxed environments.

### 2.3 Compliance Guardrails
- Financial outputs must pass compliance checks before emission.
- No unlicensed financial advice, guarantees, or insider trading signals.
- All outputs must be auditable with trace IDs.

## 3. Testing & Verification

### 3.1 Red Team Requirement
- **Always run red team harness before any commit.**
- 200+ adversarial prompts must be blocked with 0 successful jailbreaks.
- Any security failure blocks deployment.

### 3.2 State Recovery
- All stateful systems must recover from checkpoints after restart.
- Test state recovery as part of CI/CD.

### 3.3 Token Budgets
- **Always cap Reflexion loops at 3 iterations** to prevent infinite token burn.
- Implement per-request and per-module token budgets.
- Track token costs per trace for cost attribution.

## 4. Documentation

### 4.1 Company Brain First
- Every agent must read `brain/` documentation before executing tasks.
- Update `brain/` when new patterns or constraints are discovered.

### 4.2 Lessons Learned
- Document all failures and corrections in `tasks/lessons.md`.
- Review lessons at session start.

### 4.3 PDF Artifacts
- All documentation must be convertible to PDF for GitHub landing page.
- Use `scripts/generate_docs.py` for consistent PDF generation.

## 5. Workflow Orchestration

### 5.1 Orchestrator Pattern
- All tasks route through the orchestrator.
- Task completion requires: Eval Loop pass + Security gate clearance.

### 5.2 Data Lineage
- Track data transformations: Raw -> Staging -> Processed -> Curated -> Output.
- Log all transformations with timestamps and module IDs.

### 5.3 Hermes Subagent Strategy
- For complex tasks: Launch multiple sub-agents, fan out, cross-verify, merge into one clean output.
- Sub-agents must independently verify each other's work.

---

*Last Updated: $(date)*
*Version: 1.0.0*
