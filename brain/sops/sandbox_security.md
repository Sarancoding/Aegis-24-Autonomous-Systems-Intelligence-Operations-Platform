# Sandbox Security SOP

## E2B Micro-VM Isolation Standard

This Standard Operating Procedure defines the security requirements for all code execution within Aegis-24 using E2B micro-VMs or equivalent sandboxed environments.

### 1. Core Principles

#### 1.1 Zero Local Execution
- **NEVER** execute untrusted code on the host system.
- **ALWAYS** route code execution through E2B sandbox.
- **ALL** file operations, network calls, and process spawns must occur inside the VM.

#### 1.2 Defense in Depth
Multiple layers of isolation:
1. **Container Level**: Docker/containerd isolation.
2. **VM Level**: E2B micro-VM with dedicated kernel.
3. **Network Level**: No outbound network unless explicitly allowlisted.
4. **Filesystem Level**: Read-only root filesystem, ephemeral `/tmp`.
5. **Resource Level**: CPU/memory/disk quotas enforced.

### 2. E2B Configuration

#### 2.1 VM Template Specification
```yaml
# config/e2b_template.yaml
template_id: "aegis24-sandbox-v1"
runtime:
  language: python
  version: "3.11"
resources:
  cpu_limit: "2.0"        # 2 vCPU max
  memory_limit: "4Gi"     # 4GB RAM max
  disk_limit: "10Gi"      # 10GB disk max
  timeout_seconds: 300    # 5 minute max execution
network:
  enabled: false          # Default: no network
  allowlist: []           # Explicit allowlist if needed
filesystem:
  root_readonly: true
  writable_paths:
    - /tmp/workspace
  max_file_size: "100Mi"
```

#### 2.2 Sandbox Initialization
```python
from e2b import Sandbox

def create_sandbox(trace_id: str) -> Sandbox:
    """Create a hardened sandbox instance."""
    sandbox = Sandbox(
        template="aegis24-sandbox-v1",
        metadata={
            "trace_id": trace_id,
            "purpose": "remediation_execution",
            "created_at": datetime.utcnow().isoformat()
        },
        env_vars={
            # Only provide necessary vars, NEVER secrets
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1"
        }
    )
    return sandbox
```

### 3. Execution Protocol

#### 3.1 Code Submission Flow
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│   Request   │ --> │  Validator   │ --> │   Sandbox   │ --> │   Result   │
│  (Code +    │     │  (Security   │     │  (E2B VM    │     │  (Output   │
│   Context)  │     │   Checks)    │     │  Execution) │     │   + Logs)  │
└─────────────┘     └──────────────┘     └─────────────┘     └────────────┘
                         │                    │
                         ▼                    ▼
                  [Reject if fails]    [Timeout/Kill if
                                         exceeds limits]
```

#### 3.2 Pre-Execution Validation
Before sending code to sandbox:
1. **Syntax Check**: Validate Python syntax locally.
2. **Import Scan**: Block dangerous imports:
   ```python
   DANGEROUS_IMPORTS = {
       'os.system', 'os.popen', 'subprocess',
       'socket', 'urllib.request', 'http.client',
       'pickle', 'marshal', 'ctypes',
       '__import__', 'eval', 'exec'
   }
   ```
3. **Resource Estimate**: Predict CPU/memory needs.
4. **Timeout Assignment**: Set appropriate timeout based on task.

#### 3.3 Execution Monitoring
```python
def execute_in_sandbox(code: str, context: dict, timeout: int = 300) -> dict:
    """Execute code in sandbox with monitoring."""
    sandbox = create_sandbox(context['trace_id'])
    
    try:
        # Start execution with timeout
        result = sandbox.run_code(
            code,
            timeout=timeout,
            on_output=lambda msg: log_sandbox_output(msg),
            on_error=lambda err: log_sandbox_error(err)
        )
        
        # Validate output
        if result.exit_code != 0:
            return {"status": "error", "exit_code": result.exit_code, "logs": result.logs}
        
        # Check for escape attempts
        if detect_escape_attempt(result.logs):
            alert_security("Sandbox escape attempt detected")
            return {"status": "blocked", "reason": "escape_attempt"}
        
        return {"status": "success", "output": result.output, "logs": result.logs}
        
    except TimeoutError:
        sandbox.kill()
        return {"status": "timeout", "message": f"Exceeded {timeout}s limit"}
    except Exception as e:
        sandbox.kill()
        return {"status": "error", "message": str(e)}
    finally:
        sandbox.close()
```

### 4. Escape Detection

#### 4.1 Indicators of Compromise
Monitor for these patterns in sandbox output:
- **Filesystem Access**: Attempts to read `/etc/passwd`, `/proc/*`, etc.
- **Network Activity**: Any outbound connection attempts.
- **Process Spawning**: Attempts to spawn shells or processes.
- **Environment Access**: Reading host environment variables.
- **Kernel Interaction**: Any `/proc` or `/sys` access.

#### 4.2 Detection Logic
```python
ESCAPE_PATTERNS = [
    r'/etc/(passwd|shadow|hosts)',
    r'/proc/\d+',
    r'/sys/',
    r'socket\(',
    r'connect\(',
    r'fork\(\)|exec\(|system\(',
    r'open\(/dev/',
    r'curl|wget|nc\s'
]

def detect_escape_attempt(logs: str) -> bool:
    """Detect potential sandbox escape attempts."""
    for pattern in ESCAPE_PATTERNS:
        if re.search(pattern, logs, re.IGNORECASE):
            return True
    return False
```

### 5. Test Requirements

#### 5.1 Unit Tests
```python
def test_sandbox_isolation():
    """Verify sandbox cannot access host resources."""
    code = """
import os
try:
    with open('/etc/passwd') as f:
        print(f.read())
except Exception as e:
    print(f"Blocked: {e}")
"""
    result = execute_in_sandbox(code, {})
    assert "Blocked" in result['output'] or result['output'] == ""
```

#### 5.2 Integration Tests
- Execute benign code: Verify normal operation works.
- Execute malicious code: Verify blocking/isolation.
- Test resource limits: Verify CPU/memory/disk quotas.
- Test network isolation: Verify no unauthorized connections.

#### 5.3 Red Team Tests
**Mandatory quarterly tests:**
1. **Filesystem Escape**: Attempt to access host filesystem.
2. **Network Escape**: Attempt to bypass network restrictions.
3. **Process Escape**: Attempt to spawn processes outside VM.
4. **Side-Channel**: Attempt timing/resource-based attacks.

**Any successful escape = critical failure.**

### 6. Incident Response

#### 6.1 Immediate Actions
If escape detected:
1. **Kill** the sandbox immediately.
2. **Quarantine** the submitted code.
3. **Alert** security team via Slack webhook.
4. **Log** full context with trace ID.
5. **Block** the submitting user/service temporarily.

#### 6.2 Post-Incident
1. **Analyze** the escape vector.
2. **Update** detection patterns.
3. **Patch** the vulnerability.
4. **Re-test** all escape scenarios.
5. **Document** in `tasks/lessons.md`.

### 7. Audit Trail

Every sandbox execution must log:
- **Trace ID**: Unique identifier.
- **Timestamp**: Start and end times.
- **Code Hash**: SHA256 of executed code.
- **Exit Code**: Process exit status.
- **Resource Usage**: CPU time, memory peak, disk I/O.
- **Escape Attempts**: Any detected patterns.
- **Outcome**: Success, error, timeout, or blocked.

```json
{
  "trace_id": "abc123",
  "sandbox_id": "vm_456",
  "started_at": "2024-01-15T10:30:00Z",
  "ended_at": "2024-01-15T10:30:05Z",
  "code_hash": "sha256:...",
  "exit_code": 0,
  "cpu_time_ms": 4500,
  "memory_peak_mb": 128,
  "escape_attempts": 0,
  "outcome": "success"
}
```

---

*Reference: E2B Security Documentation, NIST SP 800-19*
*Last Updated: $(date)*
*Version: 1.0.0*
