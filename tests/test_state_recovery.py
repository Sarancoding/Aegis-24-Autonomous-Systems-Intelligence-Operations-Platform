"""
Test suite for state recovery from SQLite checkpoints.
Verifies LangGraph can resume from checkpoint after restart.
"""

import pytest
import asyncio
import os
import sqlite3
from datetime import datetime
from core.research_graph import ResearchGraph, SQLiteCheckpointer, NodeState


class TestStateRecovery:
    """Test state recovery functionality."""
    
    @pytest.fixture
    def checkpointer(self, tmp_path):
        db_path = tmp_path / "test_checkpoint.db"
        return SQLiteCheckpointer(db_path=str(db_path))
    
    @pytest.fixture
    def graph(self, tmp_path):
        db_path = tmp_path / "test_checkpoint.db"
        return ResearchGraph(checkpointer=SQLiteCheckpointer(db_path=str(db_path)))
    
    def test_save_and_load_checkpoint(self, checkpointer):
        """Test basic save and load functionality."""
        run_id = "test_run_123"
        
        state = NodeState(
            query="Test query",
            plan=["step 1", "step 2"],
            research_results=[{'step': 'step 1', 'findings': 'test'}],
            draft="# Draft",
            critique="Good",
            score=0.85,
            iteration=1,
            citations=["source1.pdf"],
            status='in_progress'
        )
        
        # Save
        checkpointer.save(run_id, state)
        
        # Load
        loaded = checkpointer.load(run_id)
        
        assert loaded is not None
        assert loaded['query'] == "Test query"
        assert loaded['score'] == 0.85
        assert loaded['iteration'] == 1
    
    def test_load_nonexistent_checkpoint(self, checkpointer):
        """Test loading a checkpoint that doesn't exist."""
        loaded = checkpointer.load("nonexistent_run")
        assert loaded is None
    
    @pytest.mark.asyncio
    async def test_graph_recovery_after_restart(self, graph, tmp_path):
        """Test that graph can recover state after simulated restart."""
        run_id = "recovery_test_456"
        
        # First execution - partial
        payload = {'query': 'Recovery test', 'run_id': run_id}
        
        # Execute one iteration
        result1 = await graph.execute(payload)
        
        # Verify checkpoint was created
        db_path = tmp_path / "test_checkpoint.db"
        assert db_path.exists()
        
        # Simulate restart by creating new graph instance with same checkpointer
        recovered_graph = ResearchGraph(
            checkpointer=SQLiteCheckpointer(db_path=str(db_path))
        )
        
        # Try to recover state
        recovered_state = await recovered_graph.recover_state(run_id)
        
        assert recovered_state is not None
        assert recovered_state['query'] == 'Recovery test'
    
    @pytest.mark.asyncio
    async def test_checkpoint_persistence(self, graph):
        """Test that checkpoints persist across operations."""
        run_id = "persistence_test_789"
        
        payload = {'query': 'Persistence test', 'run_id': run_id}
        await graph.execute(payload)
        
        # Verify we can still load the state
        state = await graph.recover_state(run_id)
        
        assert state is not None
        assert state['query'] == 'Persistence test'
    
    @pytest.mark.asyncio
    async def test_max_iteration_cap(self, graph):
        """Test that reflexion loop caps at 3 iterations."""
        run_id = "iteration_cap_test"
        
        payload = {'query': 'Iteration cap test', 'run_id': run_id}
        result = await graph.execute(payload)
        
        # Should not exceed max iterations
        assert result['iterations'] <= ResearchGraph.MAX_ITERATIONS
        assert result['iterations'] <= 3
    
    def test_database_schema(self, checkpointer):
        """Test that database schema is correct."""
        conn = sqlite3.connect(checkpointer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='checkpoints'
        """)
        
        table = cursor.fetchone()
        assert table is not None, "checkpoints table should exist"
        
        conn.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
