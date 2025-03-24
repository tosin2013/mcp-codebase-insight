"""Test isolation for ServerState.

This module provides utilities to create isolated ServerState instances for testing,
preventing state conflicts between parallel test runs.
"""

from typing import Dict, Optional
import asyncio
import uuid
import logging

from .core.state import ServerState
from .utils.logger import get_logger

logger = get_logger(__name__)

# Store of server states keyed by instance ID
_server_states: Dict[str, ServerState] = {}

def get_isolated_server_state(instance_id: Optional[str] = None) -> ServerState:
    """Get or create an isolated ServerState instance for tests.
    
    Args:
        instance_id: Optional unique ID for the server state
                   
    Returns:
        An isolated ServerState instance
    """
    global _server_states
    
    if instance_id is None:
        # Create a new ServerState without storing it
        instance_id = f"temp_{uuid.uuid4().hex}"
        
    if instance_id not in _server_states:
        logger.debug(f"Creating new isolated ServerState with ID: {instance_id}")
        _server_states[instance_id] = ServerState()
    
    return _server_states[instance_id]

async def cleanup_all_server_states():
    """Clean up all tracked server states."""
    global _server_states
    logger.debug(f"Cleaning up {len(_server_states)} isolated server states")
    
    # Make a copy of the states to avoid modification during iteration
    states_to_clean = list(_server_states.items())
    cleanup_tasks = []
    
    for instance_id, state in states_to_clean:
        try:
            logger.debug(f"Cleaning up ServerState: {instance_id}")
            if state.initialized:
                # Get active tasks before cleanup
                active_tasks = state.get_active_tasks()
                if active_tasks:
                    logger.debug(
                        f"Found {len(active_tasks)} active tasks for {instance_id}"
                    )
                
                # Schedule state cleanup with increased timeout
                cleanup_task = asyncio.create_task(
                    asyncio.wait_for(state.cleanup(), timeout=5.0)
                )
                cleanup_tasks.append((instance_id, cleanup_task))
            else:
                logger.debug(f"Skipping uninitialized ServerState: {instance_id}")
        except Exception as e:
            logger.error(
                f"Error preparing cleanup for ServerState {instance_id}: {e}",
                exc_info=True
            )
    
    # Wait for all cleanup tasks to complete
    if cleanup_tasks:
        for instance_id, task in cleanup_tasks:
            try:
                await task
                logger.debug(f"State {instance_id} cleaned up successfully")
                
                # Verify no tasks remain
                state = _server_states.get(instance_id)
                if state and state.get_task_count() > 0:
                    logger.warning(
                        f"State {instance_id} still has {state.get_task_count()} "
                        "active tasks after cleanup"
                    )
            except asyncio.TimeoutError:
                logger.warning(f"State cleanup timed out for {instance_id}")
                # Force cleanup
                state = _server_states.get(instance_id)
                if state:
                    state.initialized = False
            except Exception as e:
                logger.error(f"Error during state cleanup for {instance_id}: {e}")
    
    # Clear all states from global store
    _server_states.clear()
    logger.debug("All server states cleaned up") 