import requests
import json
import os
from typing import Dict, Any
import logging

class SIEMExporter:
    """Forwards structured JSON events to external SIEM endpoints (Splunk, Elastic, etc)."""
    
    def __init__(self):
        # In a real enterprise this comes from policy.json or env vars
        self.siem_endpoint = os.environ.get("SIEM_ENDPOINT", None)
        self.api_key = os.environ.get("SIEM_API_KEY", None)

    def send(self, event: Dict[str, Any]):
        """Non-blocking send to SIEM."""
        if not self.siem_endpoint:
            return # Local testing, no SIEM configured
            
        try:
            # We would usually use a background thread/queue to prevent blocking the CLI.
            # For this MVP, a short timeout POST works.
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                
            requests.post(self.siem_endpoint, json=event, headers=headers, timeout=2.0)
        except Exception as e:
            # Fallback to local error log. Never crash the main execution due to SIEM failure.
            logging.error(f"Failed to forward to SIEM: {e}")

siem_exporter = SIEMExporter()
