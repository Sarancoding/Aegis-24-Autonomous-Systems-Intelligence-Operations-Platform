"""
Ingestion Bus: Async event-driven ingestion with MCP connectors and Redis deduplication.
Handles webhooks, CDC events, and external data sources.
"""

import asyncio
import hashlib
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EventSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IngestionBus:
    """
    Async event-driven ingestion bus with:
    - MCP connector support
    - Redis-based deduplication (sliding window)
    - Severity classification
    - Intent routing
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.dedup_window_seconds = 300  # 5 minute sliding window
        self.event_queue = asyncio.Queue()
        self.processed_events = set()
        
    async def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming event through the ingestion pipeline."""
        try:
            # Step 1: Generate idempotency key
            event_id = self._generate_idempotency_key(event)
            
            # Step 2: Check for duplicates (Redis or in-memory)
            if await self._is_duplicate(event_id):
                logger.warning(f"Duplicate event detected: {event_id}")
                return {'status': 'duplicate', 'event_id': event_id}
            
            # Step 3: Classify severity and intent
            classification = self._classify_event(event)
            
            # Step 4: Route to appropriate module
            route = self._route_event(classification)
            
            # Step 5: Mark as processed
            await self._mark_processed(event_id)
            
            return {
                'status': 'processed',
                'event_id': event_id,
                'severity': classification['severity'],
                'intent': classification['intent'],
                'route': route,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _generate_idempotency_key(self, event: Dict[str, Any]) -> str:
        """Generate a unique key for deduplication."""
        content = json.dumps(event, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def _is_duplicate(self, event_id: str) -> bool:
        """Check if event was recently processed."""
        if self.redis_client:
            # Redis implementation
            key = f"aegis:dedup:{event_id}"
            return await self.redis_client.exists(key)
        else:
            # In-memory fallback
            return event_id in self.processed_events
    
    async def _mark_processed(self, event_id: str):
        """Mark event as processed."""
        if self.redis_client:
            key = f"aegis:dedup:{event_id}"
            await self.redis_client.setex(key, self.dedup_window_seconds, "1")
        else:
            self.processed_events.add(event_id)
            # Limit memory usage
            if len(self.processed_events) > 10000:
                # Remove oldest 1000
                for _ in range(1000):
                    self.processed_events.pop()
    
    def _classify_event(self, event: Dict[str, Any]) -> Dict[str, str]:
        """Classify event severity and intent."""
        event_type = event.get('type', 'unknown')
        source = event.get('source', 'unknown')
        
        # Simple rule-based classification (can be enhanced with ML)
        severity = EventSeverity.LOW
        intent = 'informational'
        
        if 'error' in event_type or 'failure' in event_type:
            severity = EventSeverity.HIGH
            intent = 'alert'
        
        if 'security' in event_type or 'breach' in event_type:
            severity = EventSeverity.CRITICAL
            intent = 'security_alert'
        
        if 'financial' in event_type or 'sec' in source.lower():
            severity = EventSeverity.MEDIUM
            intent = 'compliance_review'
        
        return {
            'severity': severity.value,
            'intent': intent,
            'event_type': event_type,
            'source': source
        }
    
    def _route_event(self, classification: Dict[str, str]) -> str:
        """Route event to appropriate module based on classification."""
        intent = classification['intent']
        severity = classification['severity']
        
        if intent == 'security_alert':
            return 'security_agent'
        elif intent == 'compliance_review':
            return 'research_agent'
        elif severity in ['high', 'critical']:
            return 'remediation_agent'
        else:
            return 'ingestion_agent'
    
    async def listen_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Listen for webhook events."""
        return await self.process_event(webhook_data)
    
    async def listen_cdc(self, cdc_event: Dict[str, Any]) -> Dict[str, Any]:
        """Listen for PostgreSQL CDC events."""
        # Add CDC-specific processing
        cdc_event['source'] = 'postgres_cdc'
        return await self.process_event(cdc_event)
    
    async def connect_mcp(self, mcp_server: str, config: Dict[str, Any]) -> None:
        """Connect to an MCP server."""
        logger.info(f"Connecting to MCP server: {mcp_server}")
        # MCP connection logic would go here
        pass
