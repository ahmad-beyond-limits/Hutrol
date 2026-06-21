import subprocess
import platform
import uuid
from typing import Dict, Any, Tuple
from human.safety.risk_classifier import RiskTier
from human.orchestrator.types import ExecutionResult

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
    
    ALLOWED_READ_COMMANDS = ["Get-Process", "Get-Service", "Get-ChildItem", "echo", "ping"]
    BLOCKED_COMMANDS = ["Stop-Process", "Remove-Item", "rm", "del", "Restart-Service"]

    @classmethod
    def analyze_command(cls, command: str) -> Tuple[bool, RiskTier, str]:
        """Analyzes a system command and returns (is_allowed, risk_tier, reason)."""
        cmd_base = command.split()[0] if command.strip() else ""
        
        if cmd_base in cls.BLOCKED_COMMANDS:
            return False, RiskTier.DESTRUCTIVE, f"Command '{cmd_base}' is explicitly blocked."
            
        if cmd_base in cls.ALLOWED_READ_COMMANDS:
            return True, RiskTier.READ_ONLY, "Allowed read-only command."
            
        # Default unknown commands to MUTATING_UNSCOPED to require approval
        return True, RiskTier.MUTATING_UNSCOPED, "Unknown command requires explicit approval."

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
