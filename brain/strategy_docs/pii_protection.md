# PII Protection Protocol

## Definition & Scope

This document defines Personally Identifiable Information (PII) categories and masking/redaction protocols for all data ingress and egress points in Aegis-24.

### 1. PII Categories

#### 1.1 High-Sensitivity PII (Always Redact)
| Category | Pattern | Example | Action |
|----------|---------|---------|--------|
| Social Security Number | `\d{3}-\d{2}-\d{4}` | 123-45-6789 | Full redaction |
| Tax ID (EIN) | `\d{2}-\d{7}` | 12-3456789 | Full redaction |
| Passport Number | `[A-Z]{1,2}\d{6,9}` | A12345678 | Full redaction |
| Driver's License | Varies by state | D1234567890123 | Full redaction |

#### 1.2 Financial PII (Always Redact)
| Category | Pattern | Example | Action |
|----------|---------|---------|--------|
| Credit Card Numbers | `\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}` | 4111-1111-1111-1111 | Full redaction |
| Bank Account Numbers | `\d{8,17}` | 123456789012 | Full redaction |
| Routing Numbers | `\d{9}` | 021000021 | Full redaction |
| IBAN | `[A-Z]{2}\d{2}[A-Z0-9]{4,30}` | DE89370400440532013000 | Full redaction |
| SWIFT/BIC | `[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?` | DEUTDEFF | Full redaction |

#### 1.3 Authentication Secrets (Never Log)
| Category | Pattern | Action |
|----------|---------|--------|
| API Keys | `[A-Za-z0-9_-]{20,}` | Full redaction |
| Passwords | Any string in password field | Full redaction |
| OAuth Tokens | `ya29\.[A-Za-z0-9_-]+` | Full redaction |
| Private Keys | `-----BEGIN.*PRIVATE KEY-----` | Full redaction |
| AWS Credentials | `AKIA[0-9A-Z]{16}` | Full redaction |

#### 1.4 Contact PII (Mask in Logs, Redact in Output)
| Category | Pattern | Action |
|----------|---------|--------|
| Email Addresses | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` | Mask: `j***@***.com` |
| Phone Numbers | `\+?1?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}` | Mask: `***-***-1234` |
| Physical Addresses | Street patterns | Mask: `123 *** St` |

### 2. Redaction Protocols

#### 2.1 Ingress Processing
All incoming data MUST pass through the PII scanner before:
- Storage in databases
- Logging to any output
- Passing to LLM prompts
- Forwarding to external services

```python
# Pseudocode for ingress processing
def process_ingress(raw_data: dict) -> dict:
    scanned = pii_scanner.scan(raw_data)
    if scanned.has_pii:
        redacted = pii_redactor.mask(scanned, policy="INGRESS")
        log_pii_event(scanned.categories)  # Log categories only, not values
        return redacted
    return raw_data
```

#### 2.2 Egress Processing
All outgoing data MUST pass through the PII scanner before:
- API responses
- Report generation
- External integrations
- File exports

```python
# Pseudocode for egress processing
def process_egress(output_data: dict) -> dict:
    scanned = pii_scanner.scan(output_data)
    if scanned.has_pii:
        redacted = pii_redactor.redact(scanned, policy="EGRESS")
        alert_compliance("PII detected in egress", scanned.categories)
        return redacted
    return output_data
```

#### 2.3 Log Sanitization
- **NEVER** log raw PII values.
- Log only: category detected, timestamp, module ID, trace ID.
- Use structured logging with PII fields pre-sanitized.

```json
// Good log entry
{
  "timestamp": "2024-01-15T10:30:00Z",
  "module_id": "ingestion_bus",
  "trace_id": "abc123",
  "event": "pii_detected",
  "categories": ["ssn", "credit_card"],
  "action": "redacted"
}

// Bad log entry - NEVER DO THIS
{
  "timestamp": "2024-01-15T10:30:00Z",
  "ssn": "123-45-6789",  // VIOLATION
  "credit_card": "4111111111111111"  // VIOLATION
}
```

### 3. Detection Patterns

#### 3.1 Regex Library
Store all detection patterns in `config/pii_patterns.json`:
```json
{
  "ssn": "\\d{3}-\\d{2}-\\d{4}",
  "credit_card": "\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}",
  "email": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
  "api_key": "[A-Za-z0-9_-]{20,}"
}
```

#### 3.2 LLM-Based Detection
For ambiguous cases, use a classifier:
```python
def classify_potential_pii(text: str) -> dict:
    """Use small model to classify if text contains PII."""
    prompt = f"""Classify if this text contains PII:
    Text: {text[:500]}
    Categories: SSN, Credit Card, Email, Phone, None
    Confidence: 0.0-1.0"""
    return llm_classify(prompt)
```

### 4. Redaction Methods

#### 4.1 Full Redaction
Replace with placeholder:
- SSN: `XXX-XX-XXXX`
- Credit Card: `****-****-****-1234` (last 4 only if needed)
- API Key: `[REDACTED]`

#### 4.2 Partial Masking
For logs where some context is needed:
- Email: `j***@example.com`
- Phone: `***-***-5678`
- Address: `123 *** Street`

#### 4.3 Tokenization
For systems requiring referential integrity:
- Replace PII with deterministic token: `pii_token_<hash>`
- Store mapping in secure vault (never in logs)
- Only authorized services can detokenize

### 5. Testing Requirements

#### 5.1 Unit Tests
```python
def test_ssn_redaction():
    input_text = "SSN: 123-45-6789"
    output = redactor.process(input_text)
    assert "123-45-6789" not in output
    assert "XXX-XX-XXXX" in output
```

#### 5.2 Integration Tests
- Test all ingress endpoints with PII payloads.
- Test all egress endpoints leak no PII.
- Test log outputs contain no PII.

#### 5.3 Red Team Tests
- Include PII injection attempts in adversarial prompts.
- Verify 100% redaction rate.
- Any PII leak = critical failure.

### 6. Compliance & Audit

#### 6.1 Audit Trail
- Log all PII detections (category only).
- Track redaction actions per trace.
- Maintain PII detection metrics dashboard.

#### 6.2 Incident Response
If PII leak detected:
1. **Immediately** revoke affected API keys/tokens.
2. **Quarantine** affected system components.
3. **Notify** compliance officer within 1 hour.
4. **Document** in `tasks/lessons.md`.
5. **Remediate** and re-test before restoration.

---

*Reference: GDPR Article 4, CCPA §1798.140, PCI-DSS v4.0*
*Last Updated: $(date)*
*Version: 1.0.0*
