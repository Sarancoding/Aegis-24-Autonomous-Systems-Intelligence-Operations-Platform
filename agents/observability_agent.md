# Observability Agent Profile

## Role: Observability Specialist

**Primary Responsibility:** Arize Phoenix/LangSmith instrumentation, trace-level token cost attribution, and data lineage tracking.

---

## Core Competencies

### 1. Arize Phoenix Integration
- Configure OpenInference tracing
- Capture LLM spans with metadata
- Export traces to Phoenix collector

### 2. LangSmith Instrumentation
- Set up callbacks for all LLM calls
- Track prompt/response pairs
- Monitor latency and token usage

### 3. Token Cost Attribution
- Calculate costs per module/trace
- Track input/output token breakdown
- Attribute costs to specific agents

### 4. Data Lineage Tracking
- Log all data transformations
- Track source → staging → processed → output flow
- Enable audit trail reconstruction

---

## Implementation

### Trace Metadata Schema
```python
from typing import Optional
from datetime import datetime

class TraceMetadata:
    """Standard trace metadata for all modules."""
    
    def __init__(
        self,
        module_id: str,
        trace_id: str,
        span_id: str,
        parent_span_id: Optional[str],
        operation: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        token_count: Optional[int] = None,
        cost_usd: Optional[float] = None,
        status: str = "in_progress",
        error: Optional[str] = None,
        attributes: Optional[dict] = None
    ):
        self.module_id = module_id
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.operation = operation
        self.start_time = start_time
        self.end_time = end_time
        self.token_count = token_count
        self.cost_usd = cost_usd
        self.status = status
        self.error = error
        self.attributes = attributes or {}
    
    def to_dict(self) -> dict:
        return {
            "module_id": self.module_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation": self.operation,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "token_count": self.token_count,
            "cost_usd": self.cost_usd,
            "status": self.status,
            "error": self.error,
            "attributes": self.attributes
        }
```

### Phoenix Setup Script
```python
from phoenix.session.client import Client
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from arize_phoenix.otel import SpanExporter

def setup_phoenix_tracing(endpoint: str = "http://localhost:6006"):
    """Configure Phoenix tracing."""
    
    # Set up tracer provider
    provider = TracerProvider()
    
    # Add Phoenix exporter
    exporter = SpanExporter(endpoint=endpoint)
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    
    # Set as global tracer
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer("aegis24")

# Usage in modules
tracer = setup_phoenix_tracing()

async def instrumented_operation(operation_name: str, **kwargs):
    with tracer.start_as_current_span(operation_name) as span:
        span.set_attribute("module_id", kwargs.get('module_id'))
        span.set_attribute("trace_id", kwargs.get('trace_id'))
        
        try:
            result = await execute_operation(**kwargs)
            span.set_attribute("status", "success")
            return result
        except Exception as e:
            span.set_attribute("status", "error")
            span.record_exception(e)
            raise
```

### Token Cost Calculator
```python
MODEL_PRICES = {
    "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}

def calculate_token_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate USD cost for token usage."""
    pricing = MODEL_PRICES.get(model, MODEL_PRICES["gpt-3.5-turbo"])
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000

def emit_cost_trace(module_id: str, trace_id: str, model: str, input_tokens: int, output_tokens: int):
    """Emit cost attribution trace."""
    cost = calculate_token_cost(model, input_tokens, output_tokens)
    
    emit_trace_metadata(
        module_id=module_id,
        trace_id=trace_id,
        operation="llm_call",
        token_count=input_tokens + output_tokens,
        cost_usd=cost,
        attributes={
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
    )
```

---

## Configuration Files

### harness/.env.example (Observability Section)
```bash
# Arize Phoenix Configuration
PHOENIX_HOST=localhost
PHOENIX_PORT=6006
PHOENIX_ENDPOINT=http://${PHOENIX_HOST}:${PHOENIX_PORT}

# LangSmith Configuration
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=aegis24
LANGCHAIN_TRACING_V2=true

# Token Cost Tracking
ENABLE_COST_TRACKING=true
DEFAULT_MODEL=gpt-4-turbo-preview
```

---

## Performance Requirements

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Trace Coverage | 100% | <99% |
| Latency Overhead | <5% | >10% |
| Cost Accuracy | 100% | <99% |
| Lineage Completeness | 100% | <95% |

---

## Testing Requirements

### Unit Tests
- `test_trace_metadata_serialization()`
- `test_token_cost_calculation()`
- `test_lineage_tracking()`

### Integration Tests
- `test_phoenix_trace_export()`
- `test_langsmith_callback()`
- `test_end_to_end_tracing()`

---

## Dependencies

```txt
arize-phoenix>=0.14.0
opentelemetry-api>=1.21.0
opentelemetry-sdk>=1.21.0
langchain>=0.1.0
```

---

*Version: 1.0.0*
*Last Updated: $(date)*
