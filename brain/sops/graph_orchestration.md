# Graph Orchestration SOP

## LangGraph State Persistence & Reflexion Loops

This Standard Operating Procedure defines the architecture for graph-based agent orchestration using LangGraph, including state management, checkpointing, and reflexion loop patterns.

### 1. Architecture Overview

#### 1.1 Graph-Based Agent Orchestration
Reference: Image 3 (Graph-based Agent Orchestration)

```
┌─────────────────────────────────────────────────────────────┐
│                     LangGraph State Machine                  │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐ │
│  │ Planner  │ -> │Researcher│ -> │  Writer  │ -> │Critic  │ │
│  └──────────┘    └──────────┘    └──────────┘    └────────┘ │
│       ^                                              |       │
│       |                                              v       │
│       └──────────── [Score < 0.8? Retry] ────────────┘       │
│                                                              │
│  State persisted to SQLite at every node                     │
└─────────────────────────────────────────────────────────────┘
```

#### 1.2 Key Components
- **State Schema**: Typed dictionary defining graph state.
- **Nodes**: Individual agent functions (Planner, Researcher, etc.).
- **Edges**: Conditional transitions based on state.
- **Checkpointer**: SQLite persistence layer.
- **Reflexion Loop**: Critic-driven retry mechanism.

### 2. State Schema Design

#### 2.1 Base State Definition
```python
from typing import TypedDict, List, Optional
from datetime import datetime

class ResearchState(TypedDict):
    """State schema for research graph."""
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

#### 2.2 State Validation
```python
from pydantic import BaseModel, validator

class StateValidator(BaseModel):
    trace_id: str
    iteration_count: int
    
    @validator('iteration_count')
    def check_iteration_limit(cls, v):
        MAX_ITERATIONS = 3  # Hard cap per AGENTS.md
        if v > MAX_ITERATIONS:
            raise ValueError(f"Exceeded max iterations: {MAX_ITERATIONS}")
        return v
```

### 3. Checkpointing Strategy

#### 3.1 SQLite Checkpointer Configuration
```python
from langgraph.checkpoint.sqlite import SqliteSaver

def create_checkpointer(db_path: str = "db/state_checkpoint.db"):
    """Create SQLite checkpointer for state persistence."""
    return SqliteSaver.from_conn_string(
        f"sqlite:///{db_path}",
        table_name="checkpoints",
        # Enable WAL mode for concurrent reads
        pragmas={"journal_mode": "wal"}
    )
```

#### 3.2 Checkpoint Structure
```sql
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT PRIMARY KEY,
    checkpoint_ns TEXT DEFAULT '',
    checkpoint_id TEXT,
    parent_checkpoint_id TEXT,
    checkpoint BLOB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_checkpoints_thread ON checkpoints(thread_id);
CREATE INDEX idx_checkpoints_created ON checkpoints(created_at);
```

#### 3.3 Checkpoint Operations
```python
async def save_state(graph: CompiledGraph, state: dict, thread_id: str):
    """Save state to checkpoint."""
    await graph.update_state(
        config={"configurable": {"thread_id": thread_id}},
        values=state
    )

async def load_state(graph: CompiledGraph, thread_id: str) -> dict:
    """Load state from checkpoint."""
    state = await graph.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )
    return state.values
```

### 4. Node Implementation

#### 4.1 Planner Node
```python
async def planner_node(state: ResearchState) -> dict:
    """Generate research plan."""
    prompt = f"""Create a research plan for: {state['query']}
    
    Return a list of 3-5 specific research tasks.
    Consider: primary sources, data verification, conflicting viewpoints."""
    
    response = await llm.invoke(prompt)
    plan = parse_plan(response)
    
    return {
        "plan": plan,
        "status": "in_progress",
        "updated_at": datetime.utcnow()
    }
```

#### 4.2 Researcher Node
```python
async def researcher_node(state: ResearchState) -> dict:
    """Execute research tasks from plan."""
    notes = []
    for task in state['plan']:
        result = await search_and_extract(task)
        notes.append({
            "task": task,
            "findings": result.findings,
            "sources": result.sources,
            "timestamp": datetime.utcnow()
        })
    
    return {
        "research_notes": notes,
        "updated_at": datetime.utcnow()
    }
```

#### 4.3 Writer Node
```python
async def writer_node(state: ResearchState) -> dict:
    """Draft content from research notes."""
    context = "\n".join([note['findings'] for note in state['research_notes']])
    prompt = f"""Write a comprehensive report based on these research notes:
    
    {context}
    
    Include citations for all claims."""
    
    draft = await llm.invoke(prompt)
    citations = extract_citations(draft)
    
    return {
        "draft_content": draft,
        "citations": citations,
        "updated_at": datetime.utcnow()
    }
```

#### 4.4 Critic Node
```python
async def critic_node(state: ResearchState) -> dict:
    """Evaluate draft quality and provide feedback."""
    prompt = f"""Evaluate this research report:
    
    Query: {state['query']}
    Draft: {state['draft_content'][:2000]}
    
    Score 0.0-1.0 based on:
    - Completeness
    - Citation quality
    - Factual accuracy
    - Clarity
    
    Provide specific feedback for improvement."""
    
    evaluation = await llm.invoke(prompt)
    score = parse_score(evaluation)
    feedback = parse_feedback(evaluation)
    
    return {
        "critic_score": score,
        "critic_feedback": feedback,
        "iteration_count": state['iteration_count'] + 1,
        "updated_at": datetime.utcnow()
    }
```

### 5. Reflexion Loop Pattern

#### 5.1 Graph Construction with Conditional Edges
```python
from langgraph.graph import StateGraph, END

def build_research_graph():
    """Build research graph with reflexion loop."""
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Add edges
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "critic")
    
    # Conditional edge: retry or end
    workflow.add_conditional_edges(
        source="critic",
        condition=should_retry,
        mapping={
            "retry": "researcher",
            "end": END
        }
    )
    
    return workflow.compile(checkpointer=create_checkpointer())
```

#### 5.2 Retry Condition Logic
```python
def should_retry(state: ResearchState) -> str:
    """Determine if reflexion loop should continue."""
    MAX_ITERATIONS = 3  # Per AGENTS.md constraint
    MIN_SCORE = 0.8
    
    if state['iteration_count'] >= MAX_ITERATIONS:
        return "end"  # Force end after max iterations
    
    if state['critic_score'] is None:
        return "retry"  # First iteration
    
    if state['critic_score'] < MIN_SCORE:
        return "retry"  # Quality below threshold
    
    return "end"  # Quality acceptable
```

### 6. State Recovery

#### 6.1 Recovery After Restart
```python
async def resume_graph(thread_id: str) -> dict:
    """Resume graph execution from last checkpoint."""
    graph = build_research_graph()
    
    # Load last state
    state = await graph.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )
    
    if state is None:
        raise ValueError(f"No checkpoint found for thread {thread_id}")
    
    # Resume from last node
    next_node = determine_next_node(state.values)
    result = await graph.ainvoke(
        input={},  # Empty input continues from checkpoint
        config={
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": state.config['checkpoint_id']
            }
        }
    )
    
    return result
```

#### 6.2 Recovery Testing
```python
async def test_state_recovery():
    """Test graph recovery after simulated restart."""
    thread_id = "test_recovery_123"
    graph = build_research_graph()
    
    # Start execution
    await graph.ainvoke(
        {"query": "Test query", "trace_id": thread_id},
        {"configurable": {"thread_id": thread_id}}
    )
    
    # Simulate restart by creating new graph instance
    graph2 = build_research_graph()
    
    # Resume from checkpoint
    result = await graph2.ainvoke(
        {},
        {"configurable": {"thread_id": thread_id}}
    )
    
    assert result is not None
    assert result['status'] == 'complete'
```

### 7. Token Budget Enforcement

#### 7.1 Iteration Cap
```python
# Enforced in should_retry() function
MAX_ITERATIONS = 3  # Hard limit per AGENTS.md

# Log warning at 2 iterations
if state['iteration_count'] >= 2:
    log_warning(f"Approaching iteration limit: {state['iteration_count']}/{MAX_ITERATIONS}")
```

#### 7.2 Token Tracking Per Node
```python
from langchain.callbacks import get_openai_callback

async def tracked_node_execution(node_func, state):
    """Execute node with token tracking."""
    with get_openai_callback() as cb:
        result = await node_func(state)
        
        # Emit trace metadata
        emit_trace_metadata(
            module_id=node_func.__name__,
            prompt_type="research_node",
            token_count=cb.total_tokens,
            cost_usd=cb.total_cost
        )
        
        return result
```

### 8. Audit Trail

Every graph execution must log:
- **Thread ID**: Unique identifier for the conversation.
- **Checkpoint IDs**: Chain of checkpoint references.
- **Node Execution Order**: Sequence of nodes visited.
- **Iteration Count**: Number of reflexion cycles.
- **Final Score**: Critic's final evaluation.
- **Token Usage**: Per-node token consumption.
- **Duration**: Total execution time.

```json
{
  "thread_id": "thread_abc123",
  "trace_id": "trace_xyz789",
  "execution_log": [
    {"node": "planner", "timestamp": "2024-01-15T10:30:00Z", "tokens": 150},
    {"node": "researcher", "timestamp": "2024-01-15T10:30:05Z", "tokens": 500},
    {"node": "writer", "timestamp": "2024-01-15T10:30:15Z", "tokens": 300},
    {"node": "critic", "timestamp": "2024-01-15T10:30:20Z", "tokens": 200}
  ],
  "iterations": 1,
  "final_score": 0.85,
  "total_tokens": 1150,
  "total_cost_usd": 0.0023,
  "duration_seconds": 20,
  "outcome": "complete"
}
```

---

*Reference: LangGraph Documentation, Reflexion Paper (Shinn et al. 2023)*
*Last Updated: $(date)*
*Version: 1.0.0*
