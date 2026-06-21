from abc import ABC, abstractmethod
from typing import List, Dict, Any
import platform
import socket
import os
from human.orchestrator.types import ToolCallRequest

class LLMProvider(ABC):
    def get_system_context(self) -> str:
        try:
            username = os.getlogin()
        except Exception:
            username = "User"
            
        return (
            f"OS: {platform.system()} {platform.release()} (Version {platform.version()}) | "
            f"Architecture: {platform.machine()} | "
            f"PC Name: {socket.gethostname()} | "
            f"Current User: {username}"
        )

    @abstractmethod
    def generate_plan(self, prompt: str, tools: List[Dict[str, Any]]) -> str | ToolCallRequest:
        """
        Generates a plan or executes a tool call based on the user prompt and available tools.
        Returns a string response or a ToolCallRequest.
        """
        pass
