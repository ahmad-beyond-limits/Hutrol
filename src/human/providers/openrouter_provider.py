import json
from typing import List, Dict, Any
from openai import OpenAI
from human.providers.base import LLMProvider
from human.orchestrator.types import ToolCallRequest

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.model = model
        # OpenRouter uses the OpenAI SDK but with a different base URL
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def generate_plan(self, prompt: str, tools: List[Dict[str, Any]]) -> str | ToolCallRequest:
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the provided tools to fulfill the user's request if necessary."},
            {"role": "user", "content": prompt}
        ]
        
        # OpenRouter supports tool calling similarly to OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else "none"
        )
        
        message = response.choices[0].message
        
        # Check if the model decided to call a tool
        if message.tool_calls and len(message.tool_calls) > 0:
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            return ToolCallRequest(name=function_name, arguments=arguments)
            
        # Otherwise return the string content
        return message.content or ""
