import json
import time
from pathlib import Path
from typing import Dict, Any
from human.compliance.export_siem import siem_exporter

class AuditLogger:
    def __init__(self):
        # Store in user's home directory
        self.audit_dir = Path.home() / ".human"
        self.audit_file = self.audit_dir / "audit.jsonl"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        if not self.audit_file.exists():
            self.audit_file.touch()

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Logs an event to the immutable audit file and forwards to SIEM."""
        log_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data
        }
        
        # 1. Local Immutable Audit
        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        # 2. External SIEM Forwarder
        siem_exporter.send(log_entry)

audit_logger = AuditLogger()
