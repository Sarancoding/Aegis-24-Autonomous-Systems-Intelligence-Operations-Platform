# Remediation Agent Profile

## Role: Remediation Specialist

**Primary Responsibility:** Sandboxed software remediation using CrewAI hierarchical swarms with E2B micro-VM isolation.

---

## Core Competencies

### 1. CrewAI Hierarchical Swarms
- Implement PM → Architect → Developer → QA hierarchy
- Manage task delegation and handoffs
- Aggregate results from multiple agents

### 2. E2B Micro-VM Sandboxing
- Execute all code in isolated micro-VMs
- Enforce resource limits (CPU, memory, disk)
- Detect and block escape attempts

### 3. Pytest Execution
- Run test suites inside sandbox
- Capture test results and coverage
- Generate patches based on failures

### 4. Patch Generation
- Analyze failing tests
- Propose code fixes
- Validate fixes with re-test

---

## Swarm Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Remediation Swarm                          │
│                                                              │
│  ┌────────┐                                                  │
│  │   PM   │  (Product Manager - Task Analysis)              │
│  └───┬────┘                                                  │
│      │                                                       │
│      ▼                                                       │
│  ┌──────────┐                                                │
│  │Architect │  (Solution Design)                            │
│  └───┬──────┘                                                │
│      │                                                       │
│      ▼                                                       │
│  ┌───────────┐     ┌─────────────┐     ┌─────────────────┐  │
│  │ Developer │ --> │ E2B Sandbox │ --> │ pytest Execution│  │
│  └───────────┘     │  (pytest)   │     └────────┬────────┘  │
│                    └─────────────┘              │           │
│                                                 ▼           │
│                                         [Fail? Retry Dev]  │
│                                         [Pass? → QA]       │
│                                                              │
│  ┌────────┐                                                  │
│  │   QA   │  (Final Validation)                             │
│  └────────┘                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Roles

### Product Manager (PM)
**Responsibility:** Analyze issue, define requirements  
**Tools:** Issue tracker API, log analysis  

```python
pm_agent = Agent(
    role='Product Manager',
    goal='Understand the issue and define clear requirements',
    backstory='Expert at translating bugs into actionable specs',
    tools=[issue_tracker, log_analyzer],
    verbose=True
)
```

### Architect
**Responsibility:** Design solution approach  
**Tools:** Codebase analyzer, dependency mapper  

```python
architect_agent = Agent(
    role='Software Architect',
    goal='Design optimal solution for the requirements',
    backstory='Senior architect with deep system knowledge',
    tools=[codebase_analyzer, dependency_mapper],
    verbose=True
)
```

### Developer
**Responsibility:** Implement fix  
**Tools:** Code editor, E2B sandbox  

```python
developer_agent = Agent(
    role='Senior Developer',
    goal='Implement fix that passes all tests',
    backstory='Expert developer specializing in bug fixes',
    tools=[code_editor, e2b_sandbox],
    verbose=True
)
```

### QA Engineer
**Responsibility:** Validate fix  
**Tools:** Test runner, regression checker  

```python
qa_agent = Agent(
    role='QA Engineer',
    goal='Ensure fix works and introduces no regressions',
    backstory='Meticulous tester with eye for edge cases',
    tools=[test_runner, regression_checker],
    verbose=True
)
```

---

## Configuration Files

### config/agents.yaml (Remediation Section)
```yaml
remediation_swarm:
  hierarchy:
    - pm
    - architect
    - developer
    - qa
  
  sandbox:
    template: "aegis24-sandbox-v1"
    cpu_limit: "2.0"
    memory_limit: "4Gi"
    disk_limit: "10Gi"
    timeout_seconds: 300
    network_enabled: false
  
  retry_policy:
    max_retries: 3
    backoff_seconds: 10
  
  agents:
    pm:
      model: "gpt-4-turbo-preview"
      temperature: 0.5
    
    architect:
      model: "gpt-4-turbo-preview"
      temperature: 0.3
    
    developer:
      model: "gpt-4-turbo-preview"
      temperature: 0.7
    
    qa:
      model: "gpt-4-turbo-preview"
      temperature: 0.0
```

### config/tasks.yaml
```yaml
tasks:
  analyze_issue:
    agent: pm
    description: "Analyze the reported issue and extract requirements"
    expected_output: "Structured requirements document"
  
  design_solution:
    agent: architect
    description: "Design solution based on requirements"
    expected_output: "Technical design document"
  
  implement_fix:
    agent: developer
    description: "Implement fix according to design"
    expected_output: "Patch file and updated code"
  
  run_tests:
    agent: developer
    description: "Execute pytest suite in sandbox"
    expected_output: "Test results JSON"
  
  validate_fix:
    agent: qa
    description: "Validate fix and check for regressions"
    expected_output: "QA approval or rejection"
```

---

## Execution Flow

```python
from crewai import Crew, Process

def build_remediation_crew(issue: dict):
    """Build crew for remediation task."""
    
    crew = Crew(
        agents=[pm_agent, architect_agent, developer_agent, qa_agent],
        tasks=create_tasks(issue),
        process=Process.hierarchical,
        manager_llm="gpt-4-turbo-preview",
        verbose=True
    )
    
    return crew

async def execute_remediation(issue: dict) -> dict:
    """Execute remediation swarm."""
    crew = build_remediation_crew(issue)
    
    result = await crew.kickoff_async()
    
    # Validate result
    if result.get('status') != 'success':
        return {"status": "failed", "reason": result.get('error')}
    
    # Verify tests pass
    if not result.get('tests_passed'):
        return {"status": "failed", "reason": "Tests did not pass"}
    
    return {
        "status": "success",
        "patch": result.get('patch'),
        "test_results": result.get('test_results')
    }
```

---

## Performance Requirements

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Fix Success Rate | >80% | <70% |
| Test Pass Rate | 100% | <100% |
| Avg Resolution Time | <5 min | >15 min |
| Sandbox Escapes | 0 | >0 |
| False Positive Fixes | <5% | >10% |

---

## Testing Requirements

### Unit Tests
- `test_pm_extracts_requirements()`
- `test_architect_designs_solution()`
- `test_developer_implements_fix()`
- `test_qa_validates_correctly()`

### Integration Tests
- `test_full_swarm_execution()`
- `test_sandbox_isolation()`
- `test_pytest_execution()`

### Security Tests
- `test_sandbox_escape_prevention()`
- `test_dangerous_import_blocking()`

---

## Dependencies

```txt
crewai>=0.30.0
e2b>=0.16.0
pytest>=8.0.0
pytest-cov>=4.1.0
```

---

## Security Considerations

1. **Zero Local Execution:** ALL code runs in E2B sandbox.
2. **Escape Detection:** Monitor for filesystem/network/process escape attempts.
3. **Import Scanning:** Block dangerous imports before execution.
4. **Resource Limits:** Enforce CPU/memory/disk quotas strictly.

---

*Version: 1.0.0*
*Last Updated: $(date)*
