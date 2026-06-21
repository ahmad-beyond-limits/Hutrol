from typing import Dict, Any
from human.safety.risk_classifier import RiskTier
from human.orchestrator.types import ExecutionResult
from human.tools.registry import ToolDef, registry
from human.mcp.broker import MCPBroker

def execute_system_command(args: Dict[str, Any]) -> ExecutionResult:
    command = args.get("command", "").strip()
    if not command:
        return ExecutionResult(success=False, output="", error="No command provided by the LLM. You must specify the 'command' argument in your tool call.")
    result = MCPBroker.execute_system_command(command)
    if result.success and not result.output.strip():
        result.output = "Command executed successfully (no output)."
    return result

def get_dynamic_risk(args: Dict[str, Any]) -> RiskTier:
    """Helper to determine risk tier dynamically based on the command."""
    command = args.get("command", "")
    _, risk_tier, _ = MCPBroker.analyze_command(command)
    return risk_tier

# Note: In our current schema, RiskTier is static per tool, but for system commands
# it needs to be dynamic. For Phase 1, we register it as MUTATING_UNSCOPED to be safe, 
# but the execution gate could check it dynamically.
system_command_tool = ToolDef(
    name="run_system_command",
    description="Run a shell or powershell command on the host OS.",
    risk_tier=RiskTier.MUTATING_UNSCOPED, # Always prompt for approval for now unless explicitly safe
    dynamic_risk_evaluator=get_dynamic_risk,
    parameters_schema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The exact command to run (e.g., 'rm file.txt' or 'Get-Process')"
            }
        },
        "required": ["command"]
    },
    executor=execute_system_command
)

# Register the tool
registry.register(system_command_tool)
