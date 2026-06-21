from typing import Dict, Any, Callable
from pydantic import BaseModel
from human.safety.risk_classifier import RiskTier
from human.orchestrator.types import ExecutionResult

class ToolDef(BaseModel):
    name: str
    description: str
    risk_tier: RiskTier
    dynamic_risk_evaluator: Callable[[Dict[str, Any]], RiskTier] | None = None
    parameters_schema: Dict[str, Any]
    executor: Callable[[Dict[str, Any]], ExecutionResult]

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDef] = {}

    def register(self, tool: ToolDef):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolDef | None:
        return self._tools.get(name)

    def get_all_schemas(self) -> list[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters_schema,
                }
            }
            for t in self._tools.values()
        ]

registry = ToolRegistry()
