from typing import Dict, Any
from human.safety.risk_classifier import RiskTier
from human.orchestrator.types import ExecutionResult
from human.tools.registry import ToolDef, registry

def execute_delegate_task(args: Dict[str, Any]) -> ExecutionResult:
    from human.orchestrator.subagent import SubAgentManager
    from human.config.loader import load_config
    from human.providers.openrouter_provider import OpenRouterProvider
    
    config = load_config()
    provider = OpenRouterProvider(api_key=config["OPENROUTER_API_KEY"], model=config["OPENROUTER_MODEL"])
    manager = SubAgentManager(provider=provider)

    task = args.get("task", "")
    tools = args.get("tools", [])
    
    result = manager.spawn(task, tools)
    
    if result["success"]:
        return ExecutionResult(success=True, output=f"Sub-agent completed task ({result['attempts']} attempts).\nResult:\n{result['result']}")
    else:
        return ExecutionResult(success=False, output="", error=result["result"])

delegate_task_tool = ToolDef(
    name="delegate_task",
    description="Spawn an isolated sub-agent to handle a scoped sub-task. Use this when you need to run complex searches or multi-step logic without polluting your main context.",
    risk_tier=RiskTier.READ_ONLY, # Delegating is safe; the sub-agent will hit MCP blocks if it tries unsafe things.
    parameters_schema={
        "type": "object",
        "properties": {
            "task": {
                "type": "string",
                "description": "The specific objective for the sub-agent."
            },
            "tools": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of tool names the sub-agent is allowed to use (e.g. ['find_files'])."
            }
        },
        "required": ["task"]
    },
    executor=execute_delegate_task
)

registry.register(delegate_task_tool)
