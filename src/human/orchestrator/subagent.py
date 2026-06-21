from typing import Dict, Any, List
from human.orchestrator.state_machine import StateMachine
from human.orchestrator.context import ContextManager
from human.observability.tracing import tracer
from human.tools.registry import registry
import time

class SubAgent:
    """Isolated, ephemeral worker for specific tasks."""
    def __init__(self, provider, tool_scope: List[str], context_limit: int = 2500):
        self.provider = provider
        self.tool_scope = tool_scope
        self.context = ContextManager(token_limit=context_limit)
        
    def run(self, task: str) -> Dict[str, Any]:
        """Runs the subagent with a 3-attempt retry loop."""
        max_retries = 3
        attempts = 0
        last_error = ""
        
        while attempts < max_retries:
            attempts += 1
            with tracer.start_as_current_span(f"subagent_attempt_{attempts}"):
                # 1. Init state machine
                state_machine = StateMachine(self.provider)
                
                # We optionally inject failure history into the prompt to help it recover
                prompt = task
                if last_error:
                    prompt += f"\n\nNote: Your previous attempt failed with: {last_error}. Try a different approach or tool."
                
                # 2. Execute
                result_text = state_machine.run(prompt)
                
                # 3. Verify
                if state_machine.exec_result and not state_machine.exec_result.success:
                    last_error = state_machine.exec_result.error
                    continue # Retry
                
                # 4. Success -> Return Summarized context
                return {
                    "success": True,
                    "result": result_text[:1000], # Force summary/compression
                    "attempts": attempts
                }
                
        # 5. Failed softly
        return {
            "success": False,
            "result": f"Task failed after {max_retries} attempts. Last error: {last_error}",
            "attempts": attempts
        }

class SubAgentManager:
    """Spawns subagents."""
    def __init__(self, provider):
        self.provider = provider
        
    def spawn(self, task: str, tool_scope: List[str] = None) -> Dict[str, Any]:
        with tracer.start_as_current_span("subagent_spawn", {"task": task, "tools": tool_scope}):
            agent = SubAgent(self.provider, tool_scope or [])
            return agent.run(task)
