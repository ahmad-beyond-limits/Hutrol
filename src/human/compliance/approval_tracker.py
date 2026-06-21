import json
import time
from pathlib import Path
from typing import Dict, Any

class ApprovalTracker:
    """Maintains a historical record of all human approvals."""
    
    def __init__(self):
        self.db_path = Path.home() / ".human" / "approvals.jsonl"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def record(self, tool_name: str, args: Dict[str, Any], user: str, decision: bool):
        record = {
            "timestamp": time.time(),
            "user": user,
            "tool": tool_name,
            "args": args,
            "decision": "approved" if decision else "denied"
        }
        
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

approval_tracker = ApprovalTracker()
