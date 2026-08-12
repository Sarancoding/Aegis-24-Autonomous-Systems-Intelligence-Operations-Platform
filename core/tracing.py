"""
Tracing: Arize Phoenix/LangSmith instrumentation for observability.
Captures token costs, latency, guardrail decisions, and data lineage per trace.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class TraceStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    ESCALATED = "escalated"


@dataclass
class TokenUsage:
    """Token usage tracking."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    model: str


@dataclass
class GuardrailDecision:
    """Guardrail decision tracking."""
    input_passed: bool
    output_passed: bool
    pii_detected: bool
    injection_blocked: bool
    confidence_score: float
    escalated: bool


@dataclass
class DataLineage:
    """Track data transformation lineage."""
    source: str
    transformations: List[str]
    destination: str
    timestamp: str


@dataclass
class Trace:
    """Complete trace record."""
    trace_id: str
    module_id: str
    prompt_type: str
    start_time: str
    end_time: str
    latency_ms: float
    token_usage: TokenUsage
    guardrail_decision: Optional[GuardrailDecision]
    lineage: Optional[DataLineage]
    status: TraceStatus
    error: Optional[str]


class TracingManager:
    """
    Observability manager with:
    - Trace-level token cost attribution
    - Latency tracking
    - Guardrail decision logging
    - Data lineage tracking
    - Arize Phoenix/LangSmith compatibility
    """
    
    def __init__(self, project_name: str = "aegis-24"):
        self.project_name = project_name
        self.traces: List[Trace] = []
        self.costs_by_module: Dict[str, float] = {}
        self.lineage_graph: List[DataLineage] = []
        
        # Simulated Phoenix/LangSmith endpoint
        self.phoenix_endpoint = None
        self.langsmith_endpoint = None
    
    def start_trace(self, module_id: str, prompt_type: str) -> str:
        """Start a new trace."""
        trace_id = str(uuid.uuid4())
        logger.debug(f"Starting trace {trace_id} for module {module_id}")
        return trace_id
    
    def end_trace(
        self,
        trace_id: str,
        module_id: str,
        prompt_type: str,
        token_usage: Dict[str, Any],
        guardrail_decision: Optional[Dict[str, Any]] = None,
        lineage: Optional[Dict[str, Any]] = None,
        status: TraceStatus = TraceStatus.SUCCESS,
        error: Optional[str] = None
    ):
        """End a trace and record metrics."""
        now = datetime.utcnow()
        
        # Calculate latency (simulated)
        latency_ms = 150.0  # Would calculate from start time in production
        
        # Create token usage record
        tokens = TokenUsage(
            prompt_tokens=token_usage.get('prompt_tokens', 0),
            completion_tokens=token_usage.get('completion_tokens', 0),
            total_tokens=token_usage.get('total_tokens', 0),
            cost_usd=token_usage.get('cost_usd', 0.0),
            model=token_usage.get('model', 'unknown')
        )
        
        # Create guardrail decision record
        guardrail = None
        if guardrail_decision:
            guardrail = GuardrailDecision(
                input_passed=guardrail_decision.get('input_passed', True),
                output_passed=guardrail_decision.get('output_passed', True),
                pii_detected=guardrail_decision.get('pii_detected', False),
                injection_blocked=guardrail_decision.get('injection_blocked', False),
                confidence_score=guardrail_decision.get('confidence_score', 1.0),
                escalated=guardrail_decision.get('escalated', False)
            )
        
        # Create lineage record
        lin = None
        if lineage:
            lin = DataLineage(
                source=lineage.get('source', 'unknown'),
                transformations=lineage.get('transformations', []),
                destination=lineage.get('destination', 'unknown'),
                timestamp=now.isoformat()
            )
            self.lineage_graph.append(lin)
        
        # Create trace
        trace = Trace(
            trace_id=trace_id,
            module_id=module_id,
            prompt_type=prompt_type,
            start_time=now.isoformat(),
            end_time=now.isoformat(),
            latency_ms=latency_ms,
            token_usage=tokens,
            guardrail_decision=guardrail,
            lineage=lin,
            status=status,
            error=error
        )
        
        self.traces.append(trace)
        
        # Track costs by module
        if module_id not in self.costs_by_module:
            self.costs_by_module[module_id] = 0.0
        self.costs_by_module[module_id] += tokens.cost_usd
        
        logger.info(f"Trace {trace_id} completed: {status.value}, cost=${tokens.cost_usd:.4f}")
        
        # In production, would export to Phoenix/LangSmith here
        self._export_trace(trace)
        
        return trace_id
    
    def record_trace(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Record a trace from payload data."""
        trace_id = payload.get('trace_id', self.start_trace(
            payload.get('module_id', 'unknown'),
            payload.get('prompt_type', 'unknown')
        ))
        
        self.end_trace(
            trace_id=trace_id,
            module_id=payload.get('module_id', 'unknown'),
            prompt_type=payload.get('prompt_type', 'unknown'),
            token_usage=payload.get('token_usage', {'total_tokens': 0, 'cost_usd': 0.0}),
            guardrail_decision=payload.get('guardrail_decision'),
            lineage=payload.get('lineage'),
            status=TraceStatus(payload.get('status', 'success')),
            error=payload.get('error')
        )
        
        return {'trace_id': trace_id, 'recorded': True}
    
    def _export_trace(self, trace: Trace):
        """Export trace to observability backend."""
        # In production, this would send to:
        # - Arize Phoenix: phoenix.Client().log_trace(...)
        # - LangSmith: langsmith.Client().create_trace(...)
        
        trace_dict = {
            'trace_id': trace.trace_id,
            'module_id': trace.module_id,
            'latency_ms': trace.latency_ms,
            'token_usage': asdict(trace.token_usage),
            'status': trace.status.value,
            'timestamp': trace.start_time
        }
        
        if trace.guardrail_decision:
            trace_dict['guardrail'] = asdict(trace.guardrail_decision)
        
        if trace.lineage:
            trace_dict['lineage'] = asdict(trace.lineage)
        
        logger.debug(f"Exporting trace: {json.dumps(trace_dict)}")
    
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a trace by ID."""
        for trace in self.traces:
            if trace.trace_id == trace_id:
                return asdict(trace)
        return None
    
    def get_traces_by_module(self, module_id: str) -> List[Dict[str, Any]]:
        """Get all traces for a module."""
        return [asdict(t) for t in self.traces if t.module_id == module_id]
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary by module."""
        total_cost = sum(self.costs_by_module.values())
        return {
            'total_cost_usd': total_cost,
            'by_module': self.costs_by_module,
            'trace_count': len(self.traces)
        }
    
    def get_lineage_path(self, source: str, destination: str) -> List[Dict[str, Any]]:
        """Get lineage path from source to destination."""
        paths = []
        for lin in self.lineage_graph:
            if lin.source == source and lin.destination == destination:
                paths.append(asdict(lin))
        return paths
    
    def export_to_phoenix(self, endpoint: str):
        """Configure and export to Arize Phoenix."""
        self.phoenix_endpoint = endpoint
        logger.info(f"Configured Phoenix endpoint: {endpoint}")
        # Would initialize phoenix.Client() here
    
    def export_to_langsmith(self, api_key: str, project: str):
        """Configure and export to LangSmith."""
        self.langsmith_endpoint = f"https://api.smith.langchain.com"
        logger.info(f"Configured LangSmith project: {project}")
        # Would initialize langsmith.Client(api_key=api_key) here


async def main():
    """Test the tracing manager."""
    manager = TracingManager()
    
    # Record a sample trace
    trace_id = manager.start_trace('research_agent', 'deep_research')
    
    manager.end_trace(
        trace_id=trace_id,
        module_id='research_agent',
        prompt_type='deep_research',
        token_usage={
            'prompt_tokens': 1500,
            'completion_tokens': 800,
            'total_tokens': 2300,
            'cost_usd': 0.046,
            'model': 'gpt-4'
        },
        guardrail_decision={
            'input_passed': True,
            'output_passed': True,
            'pii_detected': False,
            'confidence_score': 0.95
        },
        lineage={
            'source': 'user_query',
            'transformations': ['embedding', 'retrieval', 'synthesis'],
            'destination': 'research_report'
        }
    )
    
    # Get cost summary
    summary = manager.get_cost_summary()
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
