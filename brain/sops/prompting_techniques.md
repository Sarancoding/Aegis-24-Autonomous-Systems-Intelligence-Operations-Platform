# Prompting Techniques Decision Tree

## Task Complexity to Computational Cost Mapping

Reference: Image 4 (Prompting Technique Selection)

This document defines the decision tree for selecting appropriate prompting techniques based on task complexity, accuracy requirements, and token budget constraints.

### 1. Technique Overview

| Technique | Token Cost | Latency | Accuracy | Best For |
|-----------|------------|---------|----------|----------|
| Single-Pass | Low | Low | Medium | Simple tasks, high confidence |
| Self-Consistency | Medium | Medium | High | Moderate complexity, verification needed |
| Tree-of-Thought | High | High | Very High | Complex reasoning, multiple paths |
| Reflexion Loop | Variable | Variable | Highest | Iterative improvement, quality gates |

### 2. Decision Tree

```
                        ┌─────────────────┐
                        │   New Task      │
                        └────────┬────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ Task Complexity Score   │
                    │ (1-10 scale)            │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
   Score 1-3                  Score 4-7               Score 8-10
   (Simple)                  (Moderate)               (Complex)
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ Single-Pass   │      │ Accuracy        │      │ Tree-of-Thought │
│ + Guardrails  │      │ Requirement?    │      │ OR              │
│               │      └────────┬────────┘      │ Reflexion Loop  │
│ Cost: ~500    │               │                │                 │
│ tokens        │      ┌────────▼────────┐      │ Cost: >5000     │
│ Latency: <1s  │      │  < 0.95         │      │ tokens          │
│               │      │  Confidence     │      │ Latency: >10s   │
│               │      └────────┬────────┘      │                 │
│               │               │                │                 │
│               │      ┌────────▼────────┐      │                 │
│               │      │ Self-Consistency│      │                 │
│               │      │ (n=3 samples)   │      │                 │
│               │      │                 │      │                 │
│               │      │ Cost: ~1500     │      │                 │
│               │      │ tokens          │      │                 │
│               │      │ Latency: ~3s    │      │                 │
│               │      └─────────────────┘      │                 │
└───────────────┘                               └─────────────────┘
```

### 3. Technique Specifications

#### 3.1 Single-Pass (Low Complexity)

**When to Use:**
- Task complexity score: 1-3
- Well-defined input/output format
- High confidence in model capability
- Token budget constrained
- Latency sensitive (< 1s required)

**Pattern:**
```python
prompt = f"""Task: {task_description}
Input: {input_data}

Provide a direct answer following this format:
{output_format}

Constraints:
- {constraint_1}
- {constraint_2}"""

response = llm.invoke(prompt, temperature=0.0)  # Deterministic
```

**Cost Estimate:**
- Input tokens: ~200-400
- Output tokens: ~100-300
- Total: ~300-700 tokens
- Latency: 0.5-1.5 seconds

**Quality Gate:**
- Run through output guardrail
- If confidence < 0.8, escalate to Self-Consistency

#### 3.2 Self-Consistency (Moderate Complexity)

**When to Use:**
- Task complexity score: 4-7
- Multiple valid approaches possible
- Verification improves accuracy
- Moderate token budget available
- Latency tolerance: 3-5 seconds

**Pattern:**
```python
N_SAMPLES = 3  # Per AGENTS.md: balance cost/accuracy

responses = []
for i in range(N_SAMPLES):
    prompt = f"""Task: {task_description}
Input: {input_data}

Think step-by-step. Show your reasoning.
Provide your final answer in format: {output_format}"""

    response = llm.invoke(prompt, temperature=0.7)  # Add variance
    responses.append(response)

# Aggregate results
final_answer = majority_vote(responses)
confidence = calculate_confidence(responses)
```

**Cost Estimate:**
- Input tokens per sample: ~300-500
- Output tokens per sample: ~200-400
- Total: ~1500-2700 tokens (3x single-pass)
- Latency: 3-5 seconds (sequential) or 1-2s (parallel)

**Quality Gate:**
- If agreement < 0.67 (2/3), escalate to Tree-of-Thought
- If confidence < 0.85, escalate to Reflexion Loop

#### 3.3 Tree-of-Thought (High Complexity)

**When to Use:**
- Task complexity score: 8-10
- Multiple solution paths exist
- Requires strategic reasoning
- High accuracy required (>0.95)
- Token budget available (>5000 tokens)

**Pattern:**
```python
def tree_of_thought(task, depth=3, breadth=3):
    """Explore multiple reasoning paths."""
    
    # Generate initial thoughts
    thoughts = generate_branches(task, n=breadth)
    
    best_path = None
    best_score = 0
    
    for thought in thoughts:
        # Evaluate this path
        path = [thought]
        score = evaluate_path(path)
        
        # Expand if promising
        if score > 0.5 and len(path) < depth:
            next_branches = generate_branches(thought, n=breadth)
            for branch in next_branches:
                path.append(branch)
                new_score = evaluate_path(path)
                if new_score > score:
                    score = new_score
        
        if score > best_score:
            best_score = score
            best_path = path
    
    return synthesize_answer(best_path)
```

**Cost Estimate:**
- Branching factor: 3
- Depth: 3
- Evaluations per level: 3, 9, 27
- Total tokens: ~5000-15000
- Latency: 10-30 seconds

**Quality Gate:**
- Path score must exceed 0.7
- Final synthesis reviewed by critic agent

#### 3.4 Reflexion Loop (Iterative Improvement)

**When to Use:**
- Task requires iterative refinement
- Quality threshold defined (e.g., critic score >= 0.8)
- Can tolerate variable latency
- Token budget allows retries (max 3 iterations)

**Pattern:**
```python
MAX_ITERATIONS = 3  # Per AGENTS.md constraint
MIN_SCORE = 0.8

state = {"draft": "", "feedback": "", "iteration": 0}

for i in range(MAX_ITERATIONS):
    # Generate or refine
    if state['feedback']:
        prompt = f"Revise based on feedback: {state['feedback']}"
        draft = llm.invoke(prompt)
    else:
        draft = llm.invoke(f"Create: {task}")
    
    # Critique
    critique = llm.invoke(f"Evaluate quality 0-1: {draft}")
    score = parse_score(critique)
    feedback = parse_feedback(critique)
    
    state = {
        "draft": draft,
        "feedback": feedback,
        "iteration": i + 1,
        "score": score
    }
    
    if score >= MIN_SCORE:
        break  # Quality achieved

return state['draft']
```

**Cost Estimate:**
- Tokens per iteration: ~1000-2000
- Max iterations: 3
- Total: ~3000-6000 tokens (worst case)
- Latency: 5-15 seconds

**Quality Gate:**
- Hard cap at 3 iterations (prevents runaway costs)
- Minimum score: 0.8
- If not achieved after 3 iterations, escalate to human review

### 4. Cost Attribution

Every LLM call must emit trace metadata:

```python
from langchain.callbacks import get_openai_callback

def execute_with_tracking(technique, task):
    with get_openai_callback() as cb:
        result = technique(task)
        
        emit_trace_metadata(
            module_id=technique.__name__,
            prompt_type=technique.__class__.__name__,
            token_count=cb.total_tokens,
            cost_usd=cb.total_cost,
            technique=technique.__class__.__name__,
            task_complexity_score=calculate_complexity(task)
        )
        
        return result
```

### 5. Dynamic Selection Algorithm

```python
def select_prompting_technique(task: dict) -> str:
    """Select optimal prompting technique based on task attributes."""
    
    complexity = calculate_complexity(task)
    accuracy_req = task.get('accuracy_requirement', 0.9)
    token_budget = task.get('token_budget', 10000)
    latency_budget = task.get('latency_budget_ms', 5000)
    
    # Rule 1: Token budget too low for complex techniques
    if token_budget < 1000:
        return "single_pass"
    
    # Rule 2: Latency too tight for multi-step
    if latency_budget < 2000:
        return "single_pass"
    
    # Rule 3: High accuracy requirement
    if accuracy_req > 0.95:
        if token_budget > 5000 and latency_budget > 10000:
            return "tree_of_thought"
        else:
            return "reflexion_loop"
    
    # Rule 4: Complexity-based selection
    if complexity <= 3:
        return "single_pass"
    elif complexity <= 7:
        return "self_consistency"
    else:
        if token_budget > 5000:
            return "tree_of_thought"
        else:
            return "reflexion_loop"
```

### 6. Testing Requirements

#### 6.1 Unit Tests
```python
def test_technique_selection():
    """Verify technique selection logic."""
    simple_task = {"complexity": 2, "accuracy": 0.9}
    assert select_prompting_technique(simple_task) == "single_pass"
    
    complex_task = {"complexity": 9, "accuracy": 0.98}
    assert select_prompting_technique(complex_task) in ["tree_of_thought", "reflexion_loop"]
```

#### 6.2 Cost Validation
```python
def test_token_budget_enforcement():
    """Verify techniques stay within budget."""
    task = {"token_budget": 1000}
    technique = select_prompting_technique(task)
    assert technique == "single_pass"  # Only technique that fits
```

---

*Reference: "Chain-of-Thought Prompting" (Wei et al. 2022), "Tree of Thoughts" (Yao et al. 2023)*
*Last Updated: $(date)*
*Version: 1.0.0*
