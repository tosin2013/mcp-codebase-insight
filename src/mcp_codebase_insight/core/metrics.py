"""Metrics collection and monitoring module."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

class MetricType(str, Enum):
    """Metric type enumeration."""
    
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class Metric(BaseModel):
    """Metric model."""
    
    name: str
    type: MetricType
    value: Union[int, float]
    labels: Optional[Dict[str, str]] = None
    timestamp: datetime

class MetricsManager:
    """Manager for system metrics."""
    
    def __init__(self, config):
        """Initialize metrics manager."""
        self.config = config
        self.enabled = config.metrics_enabled
        self.metrics_dir = config.docs_cache_dir / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.metrics: Dict[str, List[Metric]] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize metrics collection."""
        if self.initialized:
            return
            
        try:
            if not self.enabled:
                return
                
            # Load existing metrics
            for path in self.metrics_dir.glob("*.json"):
                try:
                    metric_name = path.stem
                    with open(path) as f:
                        data = json.load(f)
                        self.metrics[metric_name] = [
                            Metric(**metric) for metric in data
                        ]
                except Exception as e:
                    print(f"Error loading metric file {path}: {e}")
                    
            self.initialized = True
        except Exception as e:
            print(f"Error initializing metrics manager: {e}")
            await self.cleanup()
            raise RuntimeError(f"Failed to initialize metrics manager: {str(e)}")
    
    async def cleanup(self):
        """Clean up metrics."""
        if not self.initialized:
            return
            
        try:
            if not self.enabled:
                return
                
            # Save all metrics
            for name, metrics in self.metrics.items():
                try:
                    await self._save_metrics(name, metrics)
                except Exception as e:
                    print(f"Error saving metrics for {name}: {e}")
        except Exception as e:
            print(f"Error cleaning up metrics manager: {e}")
        finally:
            self.initialized = False
    
    async def reset(self):
        """Reset all metrics."""
        if not self.enabled:
            return
            
        # Clear in-memory metrics
        self.metrics = {}
        
        # Remove all metric files
        for path in self.metrics_dir.glob("*.json"):
            try:
                path.unlink()
            except Exception as e:
                print(f"Error removing metric file {path}: {e}")
    
    async def record_metric(
        self,
        name: str,
        type: MetricType,
        value: Union[int, float],
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a new metric value."""
        if not self.enabled:
            return
            
        metric = Metric(
            name=name,
            type=type,
            value=value,
            labels=labels,
            timestamp=datetime.utcnow()
        )
        
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(metric)
        
        # Save metrics periodically
        if len(self.metrics[name]) >= 100:
            await self._save_metrics(name, self.metrics[name])
            self.metrics[name] = []
    
    async def get_metrics(
        self,
        names: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, List[Dict]]:
        """Get metrics, optionally filtered by name and time range."""
        if not self.enabled:
            return {}
            
        result = {}
        metric_names = names or list(self.metrics.keys())
        
        for name in metric_names:
            if name not in self.metrics:
                continue
                
            metrics = self.metrics[name]
            
            # Apply time filters
            if start_time:
                metrics = [m for m in metrics if m.timestamp >= start_time]
            if end_time:
                metrics = [m for m in metrics if m.timestamp <= end_time]
                
            result[name] = [metric.model_dump() for metric in metrics]
            
        return result
    
    async def get_metric_summary(
        self,
        name: str,
        window_minutes: int = 60
    ) -> Optional[Dict]:
        """Get summary statistics for a metric."""
        if not self.enabled or name not in self.metrics:
            return None
            
        metrics = self.metrics[name]
        if not metrics:
            return None
            
        # Filter metrics within time window
        cutoff = datetime.utcnow().timestamp() - (window_minutes * 60)
        recent_metrics = [
            m for m in metrics
            if m.timestamp.timestamp() >= cutoff
        ]
        
        if not recent_metrics:
            return None
            
        values = [m.value for m in recent_metrics]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "last": values[-1]
        }
    
    async def _save_metrics(self, name: str, metrics: List[Metric]) -> None:
        """Save metrics to file."""
        metric_path = self.metrics_dir / f"{name}.json"
        with open(metric_path, "w") as f:
            json.dump(
                [metric.model_dump() for metric in metrics],
                f,
                indent=2,
                default=str
            )
