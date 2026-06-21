import subprocess
import platform
from typing import Dict, Any, Tuple
from human.safety.risk_classifier import RiskTier
from human.orchestrator.types import ExecutionResult

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
            # We use shell=True here just for demonstration. 
            # In a real app, this would be highly sanitized or passed through an AST parser.
            if platform.system() == "Windows":
                cmd_args = ["powershell", "-Command", command]
                shell_val = False
            else:
                cmd_args = command
                shell_val = True

            result = subprocess.run(
                cmd_args, 
                shell=shell_val, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                return ExecutionResult(success=True, output=result.stdout)
            else:
                return ExecutionResult(success=False, output=result.stdout, error=result.stderr)
        except subprocess.TimeoutExpired:
            return ExecutionResult(success=False, output="", error="Execution timed out after 30 seconds.")
        except Exception as e:
            return ExecutionResult(success=False, output="", error=str(e))
