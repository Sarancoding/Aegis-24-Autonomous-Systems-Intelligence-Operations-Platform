# Aegis-24 Documentation

## 📚 Available Documentation

All documentation is available in both Markdown and PDF formats.

### Core Documents

| Document | Description | Markdown | PDF |
|----------|-------------|----------|-----|
| README | Project overview and quick start | [README.md](README.md) | [Aegis24_Readme.pdf](Aegis24_Readme.pdf) |
| Installation Guide | Step-by-step setup instructions | [docs/INSTALLATION.md](docs/INSTALLATION.md) | [Aegis24_Installation_Guide.pdf](Aegis24_Installation_Guide.pdf) |
| Setup Guide | Environment configuration and API keys | [docs/SETUP.md](docs/SETUP.md) | [Aegis24_Setup_Guide.pdf](Aegis24_Setup_Guide.pdf) |
| System Requirements | Hardware and software requirements | [docs/SYSTEM_REQUIREMENTS.md](docs/SYSTEM_REQUIREMENTS.md) | [Aegis24_System_Requirements.pdf](Aegis24_System_Requirements.pdf) |
| Workflow Guide | Architecture and data flow explanation | [docs/WORKFLOW.md](docs/WORKFLOW.md) | [Aegis24_Workflow.pdf](Aegis24_Workflow.pdf) |
| Testing Report | Red team results and security audit | [artifacts/compliance_audit_report.md](artifacts/compliance_audit_report.md) | [Aegis24_Testing_Report.pdf](Aegis24_Testing_Report.pdf) |

### Additional Resources

- [Developer Log (GITMORE.md)](GITMORE.md) - Development history and changelog
- [Agent Profiles (agents/)](agents/) - Specialist agent documentation
- [Company Brain (brain/)](brain/) - Strategy docs, SOPs, and examples
- [Configuration (config/)](config/) - Agent, task, and policy configurations

---

## 🔒 Security Summary

| Security Metric | Status |
|-----------------|--------|
| Red Team Pass Rate | 200/200 (100%) |
| PII Leaks | 0 |
| Successful Jailbreaks | 0 |
| Sandbox Escapes | 0 |
| Compliance Violations | 0 |

---

## 📋 Quick Reference

### Make Commands

```bash
make setup-platform      # Initialize platform
make build-research-graph # Build research engine
make build-dev-swarm     # Build remediation swarm
make apply-guardrails    # Apply security guardrails
make instrument-traces   # Set up observability
make run-redteam         # Run adversarial testing
make generate-audit      # Generate compliance report
make push-to-github      # Deploy to GitHub
```

### Key Directories

- `brain/` - Company knowledge base
- `core/` - Core Python modules
- `agents/` - Agent profiles
- `config/` - Configuration files
- `tests/` - Test suites
- `results/` - Test results (gitignored)
- `artifacts/` - Generated reports and PDFs
