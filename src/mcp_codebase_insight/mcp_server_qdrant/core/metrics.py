from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import asyncio
import json
from pathlib import Path
import statistics

from .config import ServerConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class MetricType(Enum):
    """Type of metric."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class MetricValue:
    """Value for a metric."""
    value: float
    timestamp: datetime
    labels: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels
        }

class Metric:
    """Metric with type and values."""
    
    def __init__(
        self,
        name: str,
        type: MetricType,
        description: str,
        labels: List[str]
    ):
        """Initialize metric."""
        self.name = name
        self.type = type
        self.description = description
        self.labels = labels
        self.values: List[MetricValue] = []

    def add(self, value: float, labels: Dict[str, str]) -> None:
        """Add value to metric."""
        self.values.append(
            MetricValue(
                value=value,
                timestamp=datetime.now(),
                labels=labels
            )
        )

    def get_values(
        self,
        since: Optional[datetime] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> List[MetricValue]:
        """Get metric values with optional filters."""
        values = self.values
        
        if since:
            values = [v for v in values if v.timestamp >= since]
        
        if labels:
            values = [
                v for v in values
                if all(v.labels.get(k) == v for k, v in labels.items())
            ]
        
        return values

    def compute_stats(
        self,
        since: Optional[datetime] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """Compute statistics for metric values."""
        values = [v.value for v in self.get_values(since, labels)]
        
        if not values:
            return {}
        
        stats = {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values)
        }
        
        if len(values) > 1:
            stats["stddev"] = statistics.stdev(values)
        
        if self.type == MetricType.HISTOGRAM:
            stats["p50"] = statistics.median(values)
            stats["p90"] = statistics.quantiles(values, n=10)[-1]
            stats["p95"] = statistics.quantiles(values, n=20)[-1]
            stats["p99"] = statistics.quantiles(values, n=100)[-1]
        
        return stats

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "labels": self.labels,
            "values": [v.to_dict() for v in self.values]
        }

class MetricsCollector:
    """Collects and manages system metrics."""

    def __init__(self, config: ServerConfig):
        """Initialize metrics collector."""
        self.config = config
        self.storage_dir = config.kb_storage_dir / "metrics"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metrics
        self.metrics: Dict[str, Metric] = {}
        self._init_metrics()
        
        # Start background tasks
        self._cleanup_task = asyncio.create_task(self._cleanup_old_metrics())

    def _init_metrics(self) -> None:
        """Initialize system metrics."""
        # Task metrics
        self.add_metric(
            "task_duration_seconds",
            MetricType.HISTOGRAM,
            "Task execution duration in seconds",
            ["task_type", "status"]
        )
        self.add_metric(
            "task_count",
            MetricType.COUNTER,
            "Number of tasks executed",
            ["task_type", "status"]
        )
        
        # Cache metrics
        self.add_metric(
            "cache_hit_count",
            MetricType.COUNTER,
            "Number of cache hits",
            ["cache_type"]
        )
        self.add_metric(
            "cache_miss_count",
            MetricType.COUNTER,
            "Number of cache misses",
            ["cache_type"]
        )
        
        # Vector store metrics
        self.add_metric(
            "vector_store_query_duration_seconds",
            MetricType.HISTOGRAM,
            "Vector store query duration in seconds",
            ["operation"]
        )
        self.add_metric(
            "vector_store_query_count",
            MetricType.COUNTER,
            "Number of vector store queries",
            ["operation"]
        )
        
        # Pattern metrics
        self.add_metric(
            "pattern_match_score",
            MetricType.HISTOGRAM,
            "Pattern match similarity scores",
            ["pattern_type"]
        )
        self.add_metric(
            "pattern_usage_count",
            MetricType.COUNTER,
            "Number of pattern usages",
            ["pattern_type"]
        )
        
        # Documentation metrics
        self.add_metric(
            "doc_fetch_duration_seconds",
            MetricType.HISTOGRAM,
            "Documentation fetch duration in seconds",
            ["source_type"]
        )
        self.add_metric(
            "doc_fetch_count",
            MetricType.COUNTER,
            "Number of documentation fetches",
            ["source_type", "status"]
        )
        
        # System metrics
        self.add_metric(
            "system_memory_bytes",
            MetricType.GAUGE,
            "System memory usage in bytes",
            []
        )
        self.add_metric(
            "system_cpu_percent",
            MetricType.GAUGE,
            "System CPU usage percentage",
            []
        )

    def add_metric(
        self,
        name: str,
        type: MetricType,
        description: str,
        labels: List[str]
    ) -> None:
        """Add new metric."""
        if name in self.metrics:
            raise ValueError(f"Metric {name} already exists")
        
        self.metrics[name] = Metric(
            name=name,
            type=type,
            description=description,
            labels=labels
        )

    async def record_task(
        self,
        task_type: str,
        duration: float,
        success: bool,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record task execution metrics."""
        status = "success" if success else "error"
        labels = {"task_type": task_type, "status": status}
        
        self.metrics["task_duration_seconds"].add(duration, labels)
        self.metrics["task_count"].add(1, labels)
        
        await self._save_metrics()

    async def record_cache_access(
        self,
        hit: bool,
        cache_type: str = "default"
    ) -> None:
        """Record cache access metrics."""
        labels = {"cache_type": cache_type}
        
        if hit:
            self.metrics["cache_hit_count"].add(1, labels)
        else:
            self.metrics["cache_miss_count"].add(1, labels)
        
        await self._save_metrics()

    async def record_vector_query(
        self,
        operation: str,
        duration: float
    ) -> None:
        """Record vector store query metrics."""
        labels = {"operation": operation}
        
        self.metrics["vector_store_query_duration_seconds"].add(duration, labels)
        self.metrics["vector_store_query_count"].add(1, labels)
        
        await self._save_metrics()

    async def record_pattern_match(
        self,
        pattern_type: str,
        score: float
    ) -> None:
        """Record pattern match metrics."""
        labels = {"pattern_type": pattern_type}
        
        self.metrics["pattern_match_score"].add(score, labels)
        self.metrics["pattern_usage_count"].add(1, labels)
        
        await self._save_metrics()

    async def record_doc_fetch(
        self,
        source_type: str,
        duration: float,
        success: bool
    ) -> None:
        """Record documentation fetch metrics."""
        status = "success" if success else "error"
        labels = {"source_type": source_type, "status": status}
        
        self.metrics["doc_fetch_duration_seconds"].add(duration, labels)
        self.metrics["doc_fetch_count"].add(1, labels)
        
        await self._save_metrics()

    async def get_metrics(
        self,
        names: Optional[List[str]] = None,
        since: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get metrics with optional filters."""
        metrics = self.metrics
        if names:
            metrics = {
                name: metric
                for name, metric in metrics.items()
                if name in names
            }
        
        return {
            name: {
                "type": metric.type.value,
                "description": metric.description,
                "stats": metric.compute_stats(since=since)
            }
            for name, metric in metrics.items()
        }

    async def _save_metrics(self) -> None:
        """Save metrics to storage."""
        metrics_file = self.storage_dir / "metrics.json"
        metrics_data = {
            name: metric.to_dict()
            for name, metric in self.metrics.items()
        }
        metrics_file.write_text(json.dumps(metrics_data, indent=2))

    async def _cleanup_old_metrics(self) -> None:
        """Cleanup old metric values."""
        while True:
            try:
                cutoff = datetime.now() - timedelta(days=7)
                
                for metric in self.metrics.values():
                    metric.values = [
                        v for v in metric.values
                        if v.timestamp >= cutoff
                    ]
                
                await self._save_metrics()
                
            except Exception as e:
                logger.error(f"Error cleaning up metrics: {e}")
            
            await asyncio.sleep(3600)  # Run hourly

    async def stop(self) -> None:
        """Stop metrics collector."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
