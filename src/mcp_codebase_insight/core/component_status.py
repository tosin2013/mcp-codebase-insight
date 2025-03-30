"""Component status enumeration."""

from enum import Enum

class ComponentStatus(str, Enum):
    """Component status enumeration."""
    
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    FAILED = "failed"
    CLEANING = "cleaning"
    CLEANED = "cleaned" 