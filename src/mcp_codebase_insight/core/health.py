"""Health monitoring module."""

import asyncio
import os
import psutil
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

class HealthStatus(str, Enum):
    """Health status enumeration."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class ComponentHealth(BaseModel):
    """Component health model."""
    
    name: str
    status: HealthStatus
    message: Optional[str] = None
    last_check: datetime
    metrics: Optional[Dict[str, float]] = None

class SystemHealth(BaseModel):
    """System health model."""
    
    status: HealthStatus
    components: Dict[str, ComponentHealth]
    system_metrics: Dict[str, float]
    timestamp: datetime

class HealthManager:
    """Manager for system health monitoring."""
    
    def __init__(self, config):
        """Initialize health manager."""
        self.config = config
        self.components: Dict[str, ComponentHealth] = {}
        self.check_interval = 60  # seconds
        self.running = False
    
    async def initialize(self):
        """Initialize health monitoring."""
        self.running = True
        asyncio.create_task(self._monitor_health())
    
    async def cleanup(self):
        """Clean up health monitoring."""
        self.running = False
    
    async def check_health(self) -> SystemHealth:
        """Check system health."""
        # Update component health
        await self._check_components()
        
        # Get system metrics
        system_metrics = await self._get_system_metrics()
        
        # Determine overall status
        status = HealthStatus.HEALTHY
        if any(c.status == HealthStatus.UNHEALTHY for c in self.components.values()):
            status = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in self.components.values()):
            status = HealthStatus.DEGRADED
            
        return SystemHealth(
            status=status,
            components=self.components,
            system_metrics=system_metrics,
            timestamp=datetime.utcnow()
        )
    
    async def register_component(
        self,
        name: str,
        check_fn=None
    ) -> None:
        """Register a component for health monitoring."""
        self.components[name] = ComponentHealth(
            name=name,
            status=HealthStatus.HEALTHY,
            last_check=datetime.utcnow(),
            metrics={}
        )
    
    async def update_component_health(
        self,
        name: str,
        status: HealthStatus,
        message: Optional[str] = None,
        metrics: Optional[Dict[str, float]] = None
    ) -> None:
        """Update component health status."""
        if name not in self.components:
            return
            
        self.components[name] = ComponentHealth(
            name=name,
            status=status,
            message=message,
            last_check=datetime.utcnow(),
            metrics=metrics
        )
    
    async def _monitor_health(self):
        """Monitor system health periodically."""
        while self.running:
            try:
                await self.check_health()
            except Exception as e:
                print(f"Error monitoring health: {e}")
                
            await asyncio.sleep(self.check_interval)
    
    async def _check_components(self):
        """Check health of all registered components."""
        # Check Qdrant connection
        try:
            if hasattr(self.config, "qdrant_url"):
                await self._check_qdrant()
        except Exception as e:
            await self.update_component_health(
                "qdrant",
                HealthStatus.UNHEALTHY,
                str(e)
            )
        
        # Check disk space
        try:
            await self._check_disk_space()
        except Exception as e:
            await self.update_component_health(
                "disk",
                HealthStatus.UNHEALTHY,
                str(e)
            )
        
        # Check memory usage
        try:
            await self._check_memory()
        except Exception as e:
            await self.update_component_health(
                "memory",
                HealthStatus.UNHEALTHY,
                str(e)
            )
    
    async def _check_qdrant(self):
        """Check Qdrant connection health."""
        # TODO: Implement actual Qdrant health check
        await self.update_component_health(
            "qdrant",
            HealthStatus.HEALTHY,
            metrics={
                "response_time": 0.1
            }
        )
    
    async def _check_disk_space(self):
        """Check disk space health."""
        disk_path = self.config.docs_cache_dir
        usage = psutil.disk_usage(disk_path)
        
        status = HealthStatus.HEALTHY
        message = None
        
        # Alert if disk usage is high
        if usage.percent >= 90:
            status = HealthStatus.UNHEALTHY
            message = "Disk usage critical"
        elif usage.percent >= 80:
            status = HealthStatus.DEGRADED
            message = "Disk usage high"
            
        await self.update_component_health(
            "disk",
            status,
            message,
            metrics={
                "total_gb": usage.total / (1024 ** 3),
                "used_gb": usage.used / (1024 ** 3),
                "free_gb": usage.free / (1024 ** 3),
                "percent_used": usage.percent
            }
        )
    
    async def _check_memory(self):
        """Check memory health."""
        memory = psutil.virtual_memory()
        
        status = HealthStatus.HEALTHY
        message = None
        
        # Alert if memory usage is high
        if memory.percent >= 90:
            status = HealthStatus.UNHEALTHY
            message = "Memory usage critical"
        elif memory.percent >= 80:
            status = HealthStatus.DEGRADED
            message = "Memory usage high"
            
        await self.update_component_health(
            "memory",
            status,
            message,
            metrics={
                "total_gb": memory.total / (1024 ** 3),
                "used_gb": memory.used / (1024 ** 3),
                "free_gb": memory.available / (1024 ** 3),
                "percent_used": memory.percent
            }
        )
    
    async def _get_system_metrics(self) -> Dict[str, float]:
        """Get system metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "load_avg_1min": os.getloadavg()[0],
            "load_avg_5min": os.getloadavg()[1],
            "load_avg_15min": os.getloadavg()[2]
        }
