import requests
import platform
from typing import Dict, Any, List
from human.providers.base import LLMProvider
from human.orchestrator.types import ToolCallRequest

class OllamaProvider(LLMProvider):
    """Air-gapped Local Provider communicating with an Ollama instance."""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3"):
        self.host = host
        self.model = model
        self.api_url = f"{self.host}/api/chat"

    def generate_plan(self, prompt: str, tools: List[Dict[str, Any]]) -> str | ToolCallRequest:
        """Sends a request to local Ollama. Format adheres to Ollama's Chat API."""
        
        # Ollama supports tools as of recent versions, we pass them down
        os_info = f"{platform.system()} {platform.release()}"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"You are a helpful assistant running on a {os_info} machine. Use tools to fulfill requests. Output OS-compatible shell commands."},
                {"role": "user", "content": prompt}
            ],
            "tools": tools,
            "stream": False
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            
            message = data.get("message", {})
            
            if "tool_calls" in message and message["tool_calls"]:
                tool_call = message["tool_calls"][0]["function"]
                return ToolCallRequest(
                    name=tool_call["name"],
                    arguments=tool_call.get("arguments", {})
                )
            
            return message.get("content", "")
            
        except requests.exceptions.RequestException as e:
            return f"Error communicating with local Ollama server: {e}"
