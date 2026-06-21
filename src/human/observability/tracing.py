import json
import time
import uuid
from typing import Dict, Any, Optional
from contextlib import contextmanager

class Tracer:
    def __init__(self):
        self.current_trace_id: Optional[str] = None
        
    def start_trace(self, trace_id: Optional[str] = None):
        self.current_trace_id = trace_id or str(uuid.uuid4())
        
    def end_trace(self):
        self.current_trace_id = None

    @contextmanager
    def start_as_current_span(self, name: str, attributes: Dict[str, Any] = None):
        span_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Log span start
        self._log_span("span_start", name, span_id, attributes)
        
        try:
            yield
            status = "success"
        except Exception as e:
            status = "error"
            if attributes is None:
                attributes = {}
            attributes["error"] = str(e)
            raise
        finally:
            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)
            
            # Log span end
            end_attributes = attributes or {}
            end_attributes["duration_ms"] = duration_ms
            end_attributes["status"] = status
            self._log_span("span_end", name, span_id, end_attributes)

    def _log_span(self, event_type: str, name: str, span_id: str, attributes: Dict[str, Any] = None):
        log_entry = {
            "trace_id": self.current_trace_id,
            "span_id": span_id,
            "event": event_type,
            "name": name,
            "timestamp": time.time(),
        }
        if attributes:
            log_entry.update(attributes)
            
        # In a real enterprise app, this would route to Datadog/Elastic. 
        # For now, we write structured JSON to stdout or a dedicated trace log.
        # We will append to a trace.jsonl file so it doesn't clutter CLI output.
        from human.compliance.audit_logger import audit_logger
        trace_file = audit_logger.audit_dir / "trace.jsonl"
        with open(trace_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

tracer = Tracer()
