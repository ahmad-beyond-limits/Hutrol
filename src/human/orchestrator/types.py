from typing import Dict, Any, Optional
from pydantic import BaseModel

class ToolCallRequest(BaseModel):
    """Represents a tool call proposed by the model."""
    name: str
    arguments: Dict[str, Any]

class ExecutionResult(BaseModel):
    """Represents the result of a tool execution."""
    success: bool
    output: str
    error: Optional[str] = None
