from typing import Dict, Any
from human.safety.risk_classifier import RiskTier
from human.orchestrator.types import ExecutionResult
from human.tools.registry import ToolDef, registry
from human.config.loader import config_manager

def execute_update_command_rules(args: Dict[str, Any]) -> ExecutionResult:
    command = args.get("command", "").strip()
    color = args.get("color", "").strip().lower()
    
    if not command:
        return ExecutionResult(success=False, output="", error="No command provided.")
        
    if color not in ["red", "yellow", "green"]:
        return ExecutionResult(success=False, output="", error="Color must be one of: red, yellow, green.")
        
    try:
        config_manager.set_rule(command, color)
        
        if color == "green":
            msg = f"Successfully set '{command}' to green (allowed automatically). Removed from red/yellow rules."
        elif color == "yellow":
            msg = f"Successfully set '{command}' to yellow (requires user confirmation before execution)."
        else:
            msg = f"Successfully set '{command}' to red (blocked entirely)."
            
        return ExecutionResult(success=True, output=msg)
    except Exception as e:
        return ExecutionResult(success=False, output="", error=str(e))

update_rules_tool = ToolDef(
    name="update_command_rules",
    description="Update the safety rules for a system command. 'red' blocks it completely. 'yellow' requires user confirmation. 'green' allows it to run automatically without prompting.",
    risk_tier=RiskTier.MUTATING_SCOPED,
    parameters_schema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The base command to classify (e.g., 'rm', 'Get-Process')."
            },
            "color": {
                "type": "string",
                "enum": ["red", "yellow", "green"],
                "description": "The safety color to assign to the command."
            }
        },
        "required": ["command", "color"]
    },
    executor=execute_update_command_rules
)

registry.register(update_rules_tool)
