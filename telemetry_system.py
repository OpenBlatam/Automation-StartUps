"""
Advanced Telemetry and Observability System for Ultimate Launch Planning System
Provides comprehensive monitoring, tracing, and analytics
"""

import json
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
from enum import Enum
import hashlib
import traceback
import sys

logger = logging.getLogger(__name__)

class TelemetryLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class SpanStatus(Enum):
    STARTED = "started"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class TelemetryEvent:
    id: str
    timestamp: datetime
    level: TelemetryLevel
    source: str
    event_type: str
    message: str
    data: Dict[str, Any]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "source": self.source,
            "event_type": self.event_type,
            "message": self.message,
            "data": self.data,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id
        }

@dataclass
class Span:
    id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime]
    status: SpanStatus
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]
    duration_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "tags": self.tags,
            "logs": self.logs,
            "duration_ms": self.duration_ms
        }

class TelemetryCollector:
    """Main telemetry collection system"""
    
    def __init__(self, buffer_size: int = 10000, flush_interval: int = 30):
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.events: deque = deque(maxlen=buffer_size)
        self.spans: Dict[str, Span] = {}
        self.traces: Dict[str, List[str]] = defaultdict(list)
        self.lock = threading.RLock()
        self.exporters: List[Callable] = []
        self.filters: List[Callable] = []
        
        # Start background flush
        self._start_flush_thread()
    
    def add_exporter(self, exporter: Callable[[List[TelemetryEvent]], None]):
        """Add telemetry exporter"""
        with self.lock:
            self.exporters.append(exporter)
    
    def add_filter(self, filter_func: Callable[[TelemetryEvent], bool]):
        """Add telemetry filter"""
        with self.lock:
            self.filters.append(filter_func)
    
    def emit_event(self, level: TelemetryLevel, source: str, event_type: str, 
                   message: str, data: Dict[str, Any] = None, 
                   trace_id: str = None, span_id: str = None) -> str:
        """Emit a telemetry event"""
        event_id = str(uuid.uuid4())
        
        event = TelemetryEvent(
            id=event_id,
            timestamp=datetime.now(),
            level=level,
            source=source,
            event_type=event_type,
            message=message,
            data=data or {},
            trace_id=trace_id,
            span_id=span_id
        )
        
        # Apply filters
        if not self._should_emit(event):
            return event_id
        
        with self.lock:
            self.events.append(event)
        
        logger.debug(f"Telemetry event emitted: {event_type} from {source}")
        return event_id
    
    def start_span(self, operation_name: str, trace_id: str = None, 
                   parent_span_id: str = None, tags: Dict[str, Any] = None) -> str:
        """Start a new span"""
        span_id = str(uuid.uuid4())
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        span = Span(
            id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=datetime.now(),
            end_time=None,
            status=SpanStatus.STARTED,
            tags=tags or {},
            logs=[]
        )
        
        with self.lock:
            self.spans[span_id] = span
            self.traces[trace_id].append(span_id)
        
        return span_id
    
    def finish_span(self, span_id: str, status: SpanStatus = SpanStatus.COMPLETED, 
                    tags: Dict[str, Any] = None, logs: List[Dict[str, Any]] = None):
        """Finish a span"""
        with self.lock:
            if span_id not in self.spans:
                logger.warning(f"Span {span_id} not found")
                return
            
            span = self.spans[span_id]
            span.end_time = datetime.now()
            span.status = status
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            
            if tags:
                span.tags.update(tags)
            
            if logs:
                span.logs.extend(logs)
    
    def add_span_log(self, span_id: str, message: str, level: TelemetryLevel = TelemetryLevel.INFO,
                     data: Dict[str, Any] = None):
        """Add a log to a span"""
        with self.lock:
            if span_id not in self.spans:
                logger.warning(f"Span {span_id} not found")
                return
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level.value,
                "message": message,
                "data": data or {}
            }
            
            self.spans[span_id].logs.append(log_entry)
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace"""
        with self.lock:
            span_ids = self.traces.get(trace_id, [])
            return [self.spans[span_id] for span_id in span_ids if span_id in self.spans]
    
    def get_span(self, span_id: str) -> Optional[Span]:
        """Get a specific span"""
        with self.lock:
            return self.spans.get(span_id)
    
    def get_events_by_source(self, source: str, limit: int = 100) -> List[TelemetryEvent]:
        """Get events by source"""
        with self.lock:
            source_events = [e for e in self.events if e.source == source]
            return source_events[-limit:]
    
    def get_events_by_level(self, level: TelemetryLevel, limit: int = 100) -> List[TelemetryEvent]:
        """Get events by level"""
        with self.lock:
            level_events = [e for e in self.events if e.level == level]
            return level_events[-limit:]
    
    def _should_emit(self, event: TelemetryEvent) -> bool:
        """Check if event should be emitted based on filters"""
        for filter_func in self.filters:
            if not filter_func(event):
                return False
        return True
    
    def _start_flush_thread(self):
        """Start background flush thread"""
        def flush_loop():
            while True:
                try:
                    time.sleep(self.flush_interval)
                    self._flush_telemetry()
                except Exception as e:
                    logger.error(f"Error in telemetry flush: {e}")
        
        flush_thread = threading.Thread(target=flush_loop, daemon=True)
        flush_thread.start()
    
    def _flush_telemetry(self):
        """Flush telemetry to exporters"""
        with self.lock:
            if not self.events:
                return
            
            events_to_export = list(self.events)
            self.events.clear()
        
        for exporter in self.exporters:
            try:
                exporter(events_to_export)
            except Exception as e:
                logger.error(f"Error in telemetry exporter: {e}")

class LaunchTelemetry:
    """Specialized telemetry for launch planning"""
    
    def __init__(self, collector: TelemetryCollector):
        self.collector = collector
        self.active_traces: Dict[str, str] = {}  # operation -> trace_id
        self.lock = threading.RLock()
    
    def start_launch_trace(self, launch_id: str, operation: str) -> str:
        """Start a launch-specific trace"""
        trace_id = str(uuid.uuid4())
        
        with self.lock:
            self.active_traces[operation] = trace_id
        
        self.collector.emit_event(
            level=TelemetryLevel.INFO,
            source="launch_telemetry",
            event_type="trace_started",
            message=f"Started trace for {operation}",
            data={"launch_id": launch_id, "operation": operation},
            trace_id=trace_id
        )
        
        return trace_id
    
    def track_phase_start(self, launch_id: str, phase: str, trace_id: str = None) -> str:
        """Track launch phase start"""
        span_id = self.collector.start_span(
            operation_name=f"launch_phase_{phase}",
            trace_id=trace_id,
            tags={"launch_id": launch_id, "phase": phase, "event": "start"}
        )
        
        self.collector.emit_event(
            level=TelemetryLevel.INFO,
            source="launch_telemetry",
            event_type="phase_started",
            message=f"Started phase: {phase}",
            data={"launch_id": launch_id, "phase": phase},
            trace_id=trace_id,
            span_id=span_id
        )
        
        return span_id
    
    def track_phase_complete(self, launch_id: str, phase: str, span_id: str, 
                           success: bool, duration: float, trace_id: str = None):
        """Track launch phase completion"""
        status = SpanStatus.COMPLETED if success else SpanStatus.ERROR
        
        self.collector.finish_span(
            span_id=span_id,
            status=status,
            tags={
                "launch_id": launch_id,
                "phase": phase,
                "event": "complete",
                "success": success,
                "duration_seconds": duration
            }
        )
        
        self.collector.emit_event(
            level=TelemetryLevel.INFO if success else TelemetryLevel.ERROR,
            source="launch_telemetry",
            event_type="phase_completed",
            message=f"Completed phase: {phase} ({'success' if success else 'failed'})",
            data={
                "launch_id": launch_id,
                "phase": phase,
                "success": success,
                "duration_seconds": duration
            },
            trace_id=trace_id,
            span_id=span_id
        )
    
    def track_task_execution(self, launch_id: str, task_name: str, task_type: str,
                           trace_id: str = None) -> str:
        """Track task execution"""
        span_id = self.collector.start_span(
            operation_name=f"task_{task_name}",
            trace_id=trace_id,
            tags={
                "launch_id": launch_id,
                "task_name": task_name,
                "task_type": task_type,
                "event": "start"
            }
        )
        
        self.collector.emit_event(
            level=TelemetryLevel.INFO,
            source="launch_telemetry",
            event_type="task_started",
            message=f"Started task: {task_name}",
            data={
                "launch_id": launch_id,
                "task_name": task_name,
                "task_type": task_type
            },
            trace_id=trace_id,
            span_id=span_id
        )
        
        return span_id
    
    def track_task_complete(self, launch_id: str, task_name: str, span_id: str,
                          success: bool, duration: float, result: Any = None,
                          trace_id: str = None):
        """Track task completion"""
        status = SpanStatus.COMPLETED if success else SpanStatus.ERROR
        
        self.collector.finish_span(
            span_id=span_id,
            status=status,
            tags={
                "launch_id": launch_id,
                "task_name": task_name,
                "event": "complete",
                "success": success,
                "duration_seconds": duration
            }
        )
        
        self.collector.emit_event(
            level=TelemetryLevel.INFO if success else TelemetryLevel.ERROR,
            source="launch_telemetry",
            event_type="task_completed",
            message=f"Completed task: {task_name} ({'success' if success else 'failed'})",
            data={
                "launch_id": launch_id,
                "task_name": task_name,
                "success": success,
                "duration_seconds": duration,
                "result": str(result) if result else None
            },
            trace_id=trace_id,
            span_id=span_id
        )
    
    def track_ai_prediction(self, model_name: str, input_data: Dict[str, Any],
                          prediction: Any, confidence: float, duration: float,
                          trace_id: str = None):
        """Track AI model prediction"""
        span_id = self.collector.start_span(
            operation_name=f"ai_prediction_{model_name}",
            trace_id=trace_id,
            tags={
                "model_name": model_name,
                "confidence": confidence,
                "event": "prediction"
            }
        )
        
        self.collector.finish_span(
            span_id=span_id,
            status=SpanStatus.COMPLETED,
            tags={
                "model_name": model_name,
                "confidence": confidence,
                "duration_seconds": duration,
                "prediction_type": type(prediction).__name__
            }
        )
        
        self.collector.emit_event(
            level=TelemetryLevel.INFO,
            source="ai_telemetry",
            event_type="prediction_made",
            message=f"AI prediction made by {model_name}",
            data={
                "model_name": model_name,
                "confidence": confidence,
                "duration_seconds": duration,
                "prediction": str(prediction),
                "input_size": len(str(input_data))
            },
            trace_id=trace_id,
            span_id=span_id
        )
    
    def track_error(self, error: Exception, context: Dict[str, Any] = None,
                   trace_id: str = None, span_id: str = None):
        """Track error occurrence"""
        self.collector.emit_event(
            level=TelemetryLevel.ERROR,
            source="error_telemetry",
            event_type="error_occurred",
            message=f"Error: {type(error).__name__}: {str(error)}",
            data={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "context": context or {}
            },
            trace_id=trace_id,
            span_id=span_id
        )
    
    def track_performance_metric(self, metric_name: str, value: float, unit: str,
                               context: Dict[str, Any] = None, trace_id: str = None):
        """Track performance metric"""
        self.collector.emit_event(
            level=TelemetryLevel.INFO,
            source="performance_telemetry",
            event_type="metric_recorded",
            message=f"Performance metric: {metric_name} = {value} {unit}",
            data={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "context": context or {}
            },
            trace_id=trace_id
        )

class TelemetryExporter:
    """Base class for telemetry exporters"""
    
    def export_events(self, events: List[TelemetryEvent]):
        """Export telemetry events"""
        raise NotImplementedError
    
    def export_spans(self, spans: List[Span]):
        """Export spans"""
        raise NotImplementedError

class ConsoleExporter(TelemetryExporter):
    """Console telemetry exporter"""
    
    def export_events(self, events: List[TelemetryEvent]):
        """Export events to console"""
        for event in events:
            print(f"[{event.timestamp}] {event.level.value.upper()} {event.source}: {event.message}")
            if event.data:
                print(f"  Data: {json.dumps(event.data, indent=2)}")
    
    def export_spans(self, spans: List[Span]):
        """Export spans to console"""
        for span in spans:
            print(f"Span {span.id}: {span.operation_name} ({span.status.value})")
            if span.duration_ms:
                print(f"  Duration: {span.duration_ms:.2f}ms")
            if span.tags:
                print(f"  Tags: {json.dumps(span.tags, indent=2)}")

class FileExporter(TelemetryExporter):
    """File telemetry exporter"""
    
    def __init__(self, events_file: str = "telemetry_events.jsonl", 
                 spans_file: str = "telemetry_spans.jsonl"):
        self.events_file = events_file
        self.spans_file = spans_file
    
    def export_events(self, events: List[TelemetryEvent]):
        """Export events to file"""
        with open(self.events_file, 'a') as f:
            for event in events:
                f.write(json.dumps(event.to_dict()) + '\n')
    
    def export_spans(self, spans: List[Span]):
        """Export spans to file"""
        with open(self.spans_file, 'a') as f:
            for span in spans:
                f.write(json.dumps(span.to_dict()) + '\n')

class TelemetryAnalyzer:
    """Telemetry analysis and insights"""
    
    def __init__(self, collector: TelemetryCollector):
        self.collector = collector
    
    def analyze_trace_performance(self, trace_id: str) -> Dict[str, Any]:
        """Analyze trace performance"""
        spans = self.collector.get_trace(trace_id)
        
        if not spans:
            return {"error": "Trace not found"}
        
        total_duration = max(span.duration_ms or 0 for span in spans)
        span_count = len(spans)
        error_count = sum(1 for span in spans if span.status == SpanStatus.ERROR)
        
        # Find critical path
        critical_path = self._find_critical_path(spans)
        
        return {
            "trace_id": trace_id,
            "total_duration_ms": total_duration,
            "span_count": span_count,
            "error_count": error_count,
            "success_rate": (span_count - error_count) / span_count if span_count > 0 else 0,
            "critical_path": critical_path,
            "spans": [span.to_dict() for span in spans]
        }
    
    def _find_critical_path(self, spans: List[Span]) -> List[str]:
        """Find critical path in trace"""
        # Simple implementation - find longest duration spans
        sorted_spans = sorted(spans, key=lambda s: s.duration_ms or 0, reverse=True)
        return [span.operation_name for span in sorted_spans[:3]]
    
    def get_launch_analytics(self, launch_id: str) -> Dict[str, Any]:
        """Get analytics for a specific launch"""
        events = self.collector.get_events_by_source("launch_telemetry")
        launch_events = [e for e in events if e.data.get("launch_id") == launch_id]
        
        if not launch_events:
            return {"error": "No events found for launch"}
        
        # Analyze phases
        phase_events = [e for e in launch_events if e.event_type in ["phase_started", "phase_completed"]]
        phases = {}
        
        for event in phase_events:
            phase = event.data.get("phase")
            if phase not in phases:
                phases[phase] = {"started": None, "completed": None}
            
            if event.event_type == "phase_started":
                phases[phase]["started"] = event.timestamp
            elif event.event_type == "phase_completed":
                phases[phase]["completed"] = event.timestamp
        
        # Calculate phase durations
        phase_durations = {}
        for phase, times in phases.items():
            if times["started"] and times["completed"]:
                duration = (times["completed"] - times["started"]).total_seconds()
                phase_durations[phase] = duration
        
        # Analyze tasks
        task_events = [e for e in launch_events if e.event_type in ["task_started", "task_completed"]]
        task_stats = defaultdict(lambda: {"started": 0, "completed": 0, "failed": 0})
        
        for event in task_events:
            task_type = event.data.get("task_type", "unknown")
            if event.event_type == "task_started":
                task_stats[task_type]["started"] += 1
            elif event.event_type == "task_completed":
                if event.data.get("success", False):
                    task_stats[task_type]["completed"] += 1
                else:
                    task_stats[task_type]["failed"] += 1
        
        return {
            "launch_id": launch_id,
            "total_events": len(launch_events),
            "phase_durations": phase_durations,
            "task_statistics": dict(task_stats),
            "event_timeline": [e.to_dict() for e in launch_events[-10:]]  # Last 10 events
        }

# Global telemetry instance
_telemetry_collector = None
_launch_telemetry = None

def get_telemetry_collector() -> TelemetryCollector:
    """Get global telemetry collector instance"""
    global _telemetry_collector
    if _telemetry_collector is None:
        _telemetry_collector = TelemetryCollector()
    return _telemetry_collector

def get_launch_telemetry() -> LaunchTelemetry:
    """Get global launch telemetry instance"""
    global _launch_telemetry
    if _launch_telemetry is None:
        _launch_telemetry = LaunchTelemetry(get_telemetry_collector())
    return _launch_telemetry

# Example usage
if __name__ == "__main__":
    # Initialize telemetry
    collector = get_telemetry_collector()
    launch_telemetry = get_launch_telemetry()
    
    # Add exporters
    console_exporter = ConsoleExporter()
    file_exporter = FileExporter()
    
    collector.add_exporter(console_exporter.export_events)
    collector.add_exporter(file_exporter.export_events)
    
    # Start a launch trace
    launch_id = "launch_001"
    trace_id = launch_telemetry.start_launch_trace(launch_id, "full_launch")
    
    # Track phases
    pre_launch_span = launch_telemetry.track_phase_start(launch_id, "pre_launch", trace_id)
    time.sleep(1)  # Simulate work
    launch_telemetry.track_phase_complete(launch_id, "pre_launch", pre_launch_span, True, 1.0, trace_id)
    
    # Track tasks
    task_span = launch_telemetry.track_task_execution(launch_id, "market_research", "research", trace_id)
    time.sleep(0.5)  # Simulate work
    launch_telemetry.track_task_complete(launch_id, "market_research", task_span, True, 0.5, "Research completed", trace_id)
    
    # Track AI prediction
    launch_telemetry.track_ai_prediction("success_predictor", {"budget": 100000}, 0.85, 0.9, 0.1, trace_id)
    
    # Track performance metric
    launch_telemetry.track_performance_metric("execution_time", 1.5, "seconds", {"phase": "pre_launch"}, trace_id)
    
    # Analyze trace
    analyzer = TelemetryAnalyzer(collector)
    analysis = analyzer.analyze_trace_performance(trace_id)
    print("\nTrace Analysis:")
    print(json.dumps(analysis, indent=2))
    
    # Get launch analytics
    analytics = analyzer.get_launch_analytics(launch_id)
    print("\nLaunch Analytics:")
    print(json.dumps(analytics, indent=2))







