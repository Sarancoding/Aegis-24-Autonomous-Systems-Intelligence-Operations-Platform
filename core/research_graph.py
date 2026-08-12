"""
Research Graph: LangGraph-based stateful research with SQLite checkpointing and Reflexion loops.
Implements Planner -> Researcher -> Writer -> Critic cycle with max 3 iterations.
"""

import asyncio
import json
import logging
import sqlite3
from typing import Dict, Any, Optional, List, TypedDict, Annotated
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class NodeState(TypedDict):
    """State structure for the research graph."""
    query: str
    plan: List[str]
    research_results: List[Dict[str, Any]]
    draft: str
    critique: str
    score: float
    iteration: int
    citations: List[str]
    status: str


class ResearchNode:
    """Base class for research graph nodes."""
    
    async def execute(self, state: NodeState) -> NodeState:
        raise NotImplementedError


class PlannerNode(ResearchNode):
    """Plans the research approach."""
    
    async def execute(self, state: NodeState) -> NodeState:
        query = state.get('query', '')
        
        # Generate research plan (simplified - would use LLM in production)
        plan = [
            f"Search for primary sources on: {query}",
            "Identify regulatory requirements",
            "Gather supporting evidence",
            "Verify citations"
        ]
        
        state['plan'] = plan
        state['status'] = 'planning_complete'
        logger.info(f"Generated plan with {len(plan)} steps")
        return state


class ResearcherNode(ResearchNode):
    """Executes research tasks."""
    
    async def execute(self, state: NodeState) -> NodeState:
        plan = state.get('plan', [])
        results = []
        
        for step in plan:
            # Simulate research (would use search APIs in production)
            result = {
                'step': step,
                'findings': f"Research findings for: {step}",
                'sources': [f"source_{i}.pdf" for i in range(3)],
                'confidence': 0.85
            }
            results.append(result)
        
        state['research_results'] = results
        state['status'] = 'research_complete'
        logger.info(f"Completed {len(results)} research tasks")
        return state


class WriterNode(ResearchNode):
    """Drafts the research report."""
    
    async def execute(self, state: NodeState) -> NodeState:
        results = state.get('research_results', [])
        query = state.get('query', '')
        
        # Generate draft report
        draft = f"# Research Report: {query}\n\n"
        draft += "## Executive Summary\n\n"
        draft += "This report presents findings from autonomous research.\n\n"
        
        for i, result in enumerate(results, 1):
            draft += f"## Section {i}: {result['step']}\n\n"
            draft += f"{result['findings']}\n\n"
            draft += f"**Sources**: {', '.join(result['sources'])}\n\n"
        
        state['draft'] = draft
        state['citations'] = [s for r in results for s in r['sources']]
        state['status'] = 'draft_complete'
        logger.info("Draft report generated")
        return state


class CriticNode(ResearchNode):
    """Critiques the draft and assigns a quality score."""
    
    async def execute(self, state: NodeState) -> NodeState:
        draft = state.get('draft', '')
        iteration = state.get('iteration', 1)
        
        # Evaluate draft quality (simplified scoring)
        has_citations = len(state.get('citations', [])) > 0
        has_sections = draft.count('##') >= 2
        length_ok = len(draft) > 100
        
        # Calculate score (0-1)
        score = 0.0
        if has_citations:
            score += 0.4
        if has_sections:
            score += 0.3
        if length_ok:
            score += 0.3
        
        # Add some variance based on iteration
        score = min(1.0, score + (iteration * 0.05))
        
        critique = ""
        if score < 0.8:
            critique = "Needs improvement: Add more citations and expand analysis."
        else:
            critique = "Report meets quality standards."
        
        state['score'] = score
        state['critique'] = critique
        state['status'] = 'critique_complete'
        logger.info(f"Critique complete: score={score}")
        return state


class SQLiteCheckpointer:
    """Persists graph state to SQLite for recovery."""
    
    def __init__(self, db_path: str = 'db/state_checkpoint.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                run_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def save(self, run_id: str, state: NodeState):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        state_json = json.dumps(state)
        cursor.execute('''
            INSERT OR REPLACE INTO checkpoints (run_id, state_json, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (run_id, state_json))
        conn.commit()
        conn.close()
        logger.debug(f"Checkpoint saved: {run_id}")
    
    def load(self, run_id: str) -> Optional[NodeState]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT state_json FROM checkpoints WHERE run_id = ?', (run_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None


class ResearchGraph:
    """
    LangGraph-style stateful research engine with:
    - Planner -> Researcher -> Writer -> Critic cycle
    - Reflexion loop (max 3 iterations)
    - SQLite checkpointing for state recovery
    """
    
    MAX_ITERATIONS = 3  # Cap to prevent infinite token burn
    SCORE_THRESHOLD = 0.8
    
    def __init__(self, checkpointer: SQLiteCheckpointer = None):
        self.checkpointer = checkpointer or SQLiteCheckpointer()
        self.nodes = {
            'planner': PlannerNode(),
            'researcher': ResearcherNode(),
            'writer': WriterNode(),
            'critic': CriticNode()
        }
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the research graph."""
        query = payload.get('query', 'Unknown research topic')
        run_id = payload.get('run_id', datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        # Try to recover from checkpoint
        state = self.checkpointer.load(run_id)
        if state:
            logger.info(f"Recovered state from checkpoint: {run_id}")
        else:
            state = NodeState(
                query=query,
                plan=[],
                research_results=[],
                draft='',
                critique='',
                score=0.0,
                iteration=0,
                citations=[],
                status='initialized'
            )
        
        # Execute graph with reflexion loop
        while state['iteration'] < self.MAX_ITERATIONS:
            state['iteration'] += 1
            logger.info(f"Research iteration {state['iteration']}/{self.MAX_ITERATIONS}")
            
            # Execute nodes in sequence
            state = await self.nodes['planner'].execute(state)
            self.checkpointer.save(run_id, state)
            
            state = await self.nodes['researcher'].execute(state)
            self.checkpointer.save(run_id, state)
            
            state = await self.nodes['writer'].execute(state)
            self.checkpointer.save(run_id, state)
            
            state = await self.nodes['critic'].execute(state)
            self.checkpointer.save(run_id, state)
            
            # Check if we should continue
            if state['score'] >= self.SCORE_THRESHOLD:
                logger.info(f"Quality threshold met: {state['score']}")
                break
            
            logger.info(f"Score {state['score']} below threshold, refining...")
        
        # Final state
        return {
            'status': 'complete' if state['score'] >= self.SCORE_THRESHOLD else 'max_iterations_reached',
            'run_id': run_id,
            'query': query,
            'iterations': state['iteration'],
            'final_score': state['score'],
            'draft': state['draft'],
            'citations': state['citations'],
            'critique': state['critique']
        }
    
    async def recover_state(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Recover state from a previous run."""
        state = self.checkpointer.load(run_id)
        if state:
            return dict(state)
        return None
