# Research Agent Profile

## Role: Research Specialist

**Primary Responsibility:** Cyclic deep research with LangGraph state machines, citation verification, and quality-controlled outputs.

---

## Core Competencies

### 1. LangGraph State Machines
- Build cyclic graphs with Planner → Researcher → Writer → Critic flow
- Implement conditional edges for reflexion loops
- Manage state transitions with TypedDict schemas

### 2. SQLite Checkpointers
- Persist state at every node execution
- Enable recovery after system restarts
- Support concurrent graph executions with WAL mode

### 3. Reflexion Loops
- Critic-driven quality improvement
- Cap at 3 iterations maximum (per AGENTS.md)
- Escalate to human review if score < 0.8 after 3 cycles

### 4. Citation Verification
- Extract and validate all citations
- Ensure primary sources are referenced
- Flag unverifiable claims

---

## Graph Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Research State Machine                     │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐ │
│  │ Planner  │ -> │Researcher│ -> │  Writer  │ -> │Critic  │ │
│  └──────────┘    └──────────┘    └──────────┘    └────────┘ │
│       ^                                              |       │
│       |                                              v       │
│       └──────────── [Score < 0.8 AND Iteration < 3] ────────┘│
│                                                              │
│  State persisted to SQLite at every node                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Node Specifications

### Planner Node
**Input:** Research query  
**Output:** List of 3-5 specific research tasks  
**Token Budget:** ~500 tokens  

```python
async def planner_node(state: ResearchState) -> dict:
    """Generate research plan from query."""
    prompt = f"""Create a research plan for: {state['query']}
    
    Return 3-5 specific research tasks considering:
    - Primary sources
    - Data verification needs
    - Conflicting viewpoints
    
    Output as JSON list."""
    
    response = await llm.invoke(prompt, temperature=0.3)
    return {"plan": parse_json_list(response)}
```

### Researcher Node
**Input:** Research plan (list of tasks)  
**Output:** Research notes with findings and sources  
**Token Budget:** ~2000 tokens  

```python
async def researcher_node(state: ResearchState) -> dict:
    """Execute research tasks."""
    notes = []
    for task in state['plan']:
        result = await search_and_extract(task)
        notes.append({
            "task": task,
            "findings": result.findings,
            "sources": result.sources,
            "timestamp": datetime.utcnow()
        })
    
    return {"research_notes": notes}
```

### Writer Node
**Input:** Research notes  
**Output:** Draft content with citations  
**Token Budget:** ~1500 tokens  

```python
async def writer_node(state: ResearchState) -> dict:
    """Draft report from research notes."""
    context = "\n".join([note['findings'] for note in state['research_notes']])
    
    prompt = f"""Write a comprehensive report:
    
    Research Notes:
    {context}
    
    Requirements:
    - Include citations for all claims
    - Use markdown format
    - Add disclaimer header"""
    
    draft = await llm.invoke(prompt)
    citations = extract_citations(draft)
    
    return {
        "draft_content": draft,
        "citations": citations
    }
```

### Critic Node
**Input:** Draft content  
**Output:** Score (0.0-1.0) and feedback  
**Token Budget:** ~800 tokens  

```python
async def critic_node(state: ResearchState) -> dict:
    """Evaluate draft quality."""
    prompt = f"""Evaluate this research report:
    
    Query: {state['query']}
    Draft: {state['draft_content'][:2000]}
    
    Score 0.0-1.0 based on:
    - Completeness (25%)
    - Citation quality (25%)
    - Factual accuracy (25%)
    - Clarity (25%)
    
    Provide specific feedback for improvement."""
    
    evaluation = await llm.invoke(prompt)
    score = parse_score(evaluation)
    feedback = parse_feedback(evaluation)
    
    return {
        "critic_score": score,
        "critic_feedback": feedback,
        "iteration_count": state['iteration_count'] + 1
    }
```

---

## State Schema

```python
from typing import TypedDict, List, Optional
from datetime import datetime

class ResearchState(TypedDict):
    trace_id: str
    query: str
    plan: List[str]
    research_notes: List[dict]
    draft_content: str
    citations: List[dict]
    critic_score: Optional[float]
    critic_feedback: Optional[str]
    iteration_count: int
    created_at: datetime
    updated_at: datetime
    status: str  # 'pending', 'in_progress', 'complete', 'failed'
```

---

## Configuration Files

### config/agents.yaml (Research Section)
```yaml
research_agent:
  max_iterations: 3
  min_score_threshold: 0.8
  checkpoint_db: "db/state_checkpoint.db"
  
  nodes:
    planner:
      model: "gpt-4-turbo-preview"
      temperature: 0.3
      max_tokens: 500
    
    researcher:
      model: "gpt-4-turbo-preview"
      temperature: 0.5
      max_tokens: 2000
      search_sources:
        - "google_search_api"
        - "scholar_api"
        - "news_api"
    
    writer:
      model: "gpt-4-turbo-preview"
      temperature: 0.7
      max_tokens: 1500
    
    critic:
      model: "gpt-4-turbo-preview"
      temperature: 0.0  # Deterministic scoring
      max_tokens: 800
```

---

## Performance Requirements

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Completion Rate | >95% | <90% |
| Avg Quality Score | >0.8 | <0.7 |
| P99 Latency | <30s | >60s |
| Citation Accuracy | 100% | <99% |
| State Recovery | 100% | <99% |

---

## Testing Requirements

### Unit Tests
- `test_planner_generates_valid_plan()`
- `test_researcher_extracts_sources()`
- `test_writer_includes_citations()`
- `test_critic_provides_score()`

### Integration Tests
- `test_full_graph_execution()`
- `test_reflexion_loop_retry()`
- `test_max_iteration_cap()`

### Recovery Tests
- `test_state_recovery_after_restart()`
- `test_checkpoint_continuity()`

---

## Dependencies

```txt
langgraph>=0.0.11
langchain>=0.1.0
langchain-openai>=0.0.5
aiosqlite>=0.19.0
```

---

## Security Considerations

1. **Source Verification:** Validate all external data sources.
2. **Citation Integrity:** Never fabricate citations.
3. **Token Budget:** Enforce 3-iteration cap strictly.
4. **PII Handling:** Redact any PII in research results.

---

*Version: 1.0.0*
*Last Updated: $(date)*
