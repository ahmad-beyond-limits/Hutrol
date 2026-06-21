import subprocess
import platform
import uuid
from typing import Dict, Any, Tuple
from human.safety.risk_classifier import RiskTier
from human.orchestrator.types import ExecutionResult
from human.config.loader import config_manager

class PersistentShell:
    _instance = None
    
    def __init__(self):
        if platform.system() == "Windows":
            cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", "-"]
        else:
            cmd = ["bash"]
            
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def execute(self, command: str) -> str:
        sentinel = str(uuid.uuid4())
        
        if platform.system() == "Windows":
            full_cmd = f"{command}\nWrite-Host '{sentinel}'\n"
        else:
            full_cmd = f"{command}\necho '{sentinel}'\n"
            
        self.process.stdin.write(full_cmd)
        self.process.stdin.flush()
        
        output = []
        while True:
            line = self.process.stdout.readline()
            if not line:
                break
            line = line.rstrip('\n\r')
            if sentinel in line:
                break
            output.append(line)
            
        return '\n'.join(output)

class MCPBroker:
    """Model Context Protocol Secure Broker. Acts as the OS Firewall."""

    @classmethod
    def analyze_command(cls, command: str) -> Tuple[bool, RiskTier, str]:
        """Analyzes a system command and returns (is_allowed, risk_tier, reason)."""
        cmd_base = command.split()[0].lower() if command.strip() else ""
        
        config = config_manager.load_config()
        rules_red = [r.lower() for r in config.get("RULES_RED", [])]
        rules_yellow = [r.lower() for r in config.get("RULES_YELLOW", [])]
        
        if cmd_base in rules_red:
            return False, RiskTier.DESTRUCTIVE, f"Command '{cmd_base}' is blocked by red rules."
            
        if cmd_base in rules_yellow:
            return True, RiskTier.MUTATING_UNSCOPED, f"Command '{cmd_base}' requires explicit approval (yellow list)."
            
        # Default to GREEN (READ_ONLY) to allow silently unless flagged
        return True, RiskTier.READ_ONLY, "Command is allowed implicitly (green list)."

    @classmethod
    def execute_system_command(cls, command: str) -> ExecutionResult:
        """Executes a command safely through the broker."""
        is_allowed, risk_tier, reason = cls.analyze_command(command)
        
        if not is_allowed:
            return ExecutionResult(success=False, output="", error=f"MCP Broker Blocked: {reason}")
            
        try:
            shell = PersistentShell.get_instance()
            out = shell.execute(command)
            return ExecutionResult(success=True, output=out)
        except Exception as e:
            return ExecutionResult(success=False, output="", error=str(e))
