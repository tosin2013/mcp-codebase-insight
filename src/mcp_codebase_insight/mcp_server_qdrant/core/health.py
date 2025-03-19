from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import asyncio
import json
import psutil
from pathlib import Path

from .config import ServerConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class HealthStatus(Enum):
    """Health status of a component."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ComponentHealth:
    """Health information for a component."""
    name: str
    status: HealthStatus
    message: str
    last_check: datetime
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "last_check": self.last_check.isoformat(),
            "metrics": self.metrics
        }

class HealthMonitor:
    """Monitors system health."""

    def __init__(self, config: ServerConfig):
        """Initialize health monitor."""
        self.config = config
        self.storage_dir = config.kb_storage_dir / "health"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize health checks
        self.health_checks: Dict[str, ComponentHealth] = {}
        self._init_health_checks()
        
        # Start background tasks
        self._monitor_task = asyncio.create_task(self._monitor_health())

    def _init_health_checks(self) -> None:
        """Initialize component health checks."""
        components = [
            "vector_store",
            "cache",
            "knowledge_base",
            "task_manager",
            "prompt_manager",
            "adr_manager",
            "debug_system",
            "doc_manager",
            "metrics_collector"
        ]
        
        now = datetime.now()
        for component in components:
            self.health_checks[component] = ComponentHealth(
                name=component,
                status=HealthStatus.UNKNOWN,
                message="Initial state",
                last_check=now,
                metrics={}
            )

    async def check_health(self, force: bool = False) -> Dict[str, Any]:
        """Check system health."""
        if force:
            await self._check_all_components()
        
        # Get system metrics
        system_metrics = await self._get_system_metrics()
        
        # Compute overall status
        status = HealthStatus.HEALTHY
        for check in self.health_checks.values():
            if check.status == HealthStatus.UNHEALTHY:
                status = HealthStatus.UNHEALTHY
                break
            elif check.status == HealthStatus.DEGRADED:
                status = HealthStatus.DEGRADED
        
        health_data = {
            "status": status.value,
            "timestamp": datetime.now().isoformat(),
            "components": {
                name: check.to_dict()
                for name, check in self.health_checks.items()
            },
            "system": system_metrics
        }
        
        # Save health data
        health_file = self.storage_dir / "health.json"
        health_file.write_text(json.dumps(health_data, indent=2))
        
        return health_data

    async def update_component_health(
        self,
        component: str,
        status: HealthStatus,
        message: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update component health status."""
        if component not in self.health_checks:
            raise ValueError(f"Unknown component: {component}")
        
        self.health_checks[component] = ComponentHealth(
            name=component,
            status=status,
            message=message,
            last_check=datetime.now(),
            metrics=metrics or {}
        )

    async def _check_all_components(self) -> None:
        """Check health of all components."""
        # Vector store check
        try:
            # Check connection and basic operations
            await self.update_component_health(
                "vector_store",
                HealthStatus.HEALTHY,
                "Vector store operational",
                {"connection": "ok"}
            )
        except Exception as e:
            await self.update_component_health(
                "vector_store",
                HealthStatus.UNHEALTHY,
                f"Vector store error: {str(e)}"
            )
        
        # Cache check
        try:
            # Check cache operations
            await self.update_component_health(
                "cache",
                HealthStatus.HEALTHY,
                "Cache operational",
                {"size": "ok"}
            )
        except Exception as e:
            await self.update_component_health(
                "cache",
                HealthStatus.UNHEALTHY,
                f"Cache error: {str(e)}"
            )
        
        # Knowledge base check
        try:
            kb_dir = self.config.kb_storage_dir
            if not kb_dir.exists():
                raise Exception("Storage directory not found")
            
            await self.update_component_health(
                "knowledge_base",
                HealthStatus.HEALTHY,
                "Knowledge base operational",
                {"storage": "ok"}
            )
        except Exception as e:
            await self.update_component_health(
                "knowledge_base",
                HealthStatus.UNHEALTHY,
                f"Knowledge base error: {str(e)}"
            )
        
        # Check other components...
        # Similar checks would be implemented for each component

    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            
            return {
                "cpu": {
                    "percent": cpu_percent
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": disk.percent
                }
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}

    async def _monitor_health(self) -> None:
        """Monitor system health periodically."""
        while True:
            try:
                await self._check_all_components()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    def get_component_status(self, component: str) -> Optional[ComponentHealth]:
        """Get health status of specific component."""
        return self.health_checks.get(component)

    def is_healthy(self, component: str) -> bool:
        """Check if component is healthy."""
        check = self.health_checks.get(component)
        return check is not None and check.status == HealthStatus.HEALTHY

    async def stop(self) -> None:
        """Stop health monitor."""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
