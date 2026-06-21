from abc import ABC, abstractmethod
from typing import List, Dict, Any
from human.orchestrator.types import ToolCallRequest

class LLMProvider(ABC):
    @abstractmethod
    def generate_plan(self, prompt: str, tools: List[Dict[str, Any]]) -> str | ToolCallRequest:
        """
        Generates a plan or executes a tool call based on the user prompt and available tools.
        Returns a string response or a ToolCallRequest.
        """
        pass
