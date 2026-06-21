from enum import Enum, auto
from typing import Dict, Any, Tuple
from human.providers.base import LLMProvider
from human.tools.registry import registry
from human.orchestrator.types import ToolCallRequest, ExecutionResult
from human.safety.approval_gate import ApprovalGate
from human.observability.tracing import tracer
from human.memory.sqlite_store import sqlite_store
from human.orchestrator.context import ContextManager
from human.compliance.audit_logger import audit_logger
from human.compliance.policy_engine import policy_engine
from human.compliance.approval_tracker import approval_tracker

class OrchestratorState(Enum):
    PARSE = auto()
    PLAN = auto()
    RISK_CHECK = auto()
    APPROVAL = auto()
    EXECUTE = auto()
    VERIFY = auto()
    REPORT = auto()
    END = auto()

class StateMachine:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.state = OrchestratorState.PARSE
        
        # Context variables
        self.prompt = ""
        self.plan_result = None
        self.tool_def = None
        self.tool_args = {}
        self.current_risk = None
        self.exec_result = None
        self.final_report = ""
        self.history = []

    def run(self, prompt: str) -> str:
        self.prompt = prompt
        self.state = OrchestratorState.PARSE
        
        # Add user prompt to history
        self.history.append({"role": "user", "content": prompt})
        
        while self.state != OrchestratorState.END:
            self._tick()
            
        # Add agent response to history
        self.history.append({"role": "assistant", "content": self.final_report})
            
        return self.final_report

    def _tick(self):
        if self.state == OrchestratorState.PARSE:
            audit_logger.log_event("PARSE_START", {"prompt": self.prompt})
            self.state = OrchestratorState.PLAN
            
        elif self.state == OrchestratorState.PLAN:
            with tracer.start_as_current_span("model_plan"):
                schemas = registry.get_all_schemas()
                
                # Format history for the prompt
                context_prompt = self.prompt
                if len(self.history) > 1:
                    # Ignore the last item since it's the current prompt
                    history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.history[:-1]])
                    context_prompt = f"Previous Conversation Context:\n{history_text}\n\nUser's Current Request:\n{self.prompt}"
                
                self.plan_result = self.provider.generate_plan(context_prompt, tools=schemas)
                
            audit_logger.log_event("PLAN_COMPLETE", {"plan": str(self.plan_result)})
            
            if isinstance(self.plan_result, str):
                self.final_report = self.plan_result
                self.state = OrchestratorState.END
            else:
                self.state = OrchestratorState.RISK_CHECK
                
        elif self.state == OrchestratorState.RISK_CHECK:
            tool_name = self.plan_result.name
            self.tool_args = self.plan_result.arguments
            self.tool_def = registry.get_tool(tool_name)
            
            if not self.tool_def:
                self.final_report = f"Error: Tool '{tool_name}' not found."
                audit_logger.log_event("RISK_CHECK_FAILED", {"error": self.final_report})
                self.state = OrchestratorState.END
            else:
                if self.tool_def.dynamic_risk_evaluator:
                    self.current_risk = self.tool_def.dynamic_risk_evaluator(self.tool_args)
                else:
                    self.current_risk = self.tool_def.risk_tier
                    
                decision = policy_engine.evaluate(tool_name, self.tool_args, self.current_risk)
                audit_logger.log_event("POLICY_DECISION", {"tool": tool_name, "decision": decision})
                
                if decision == "block":
                    self.final_report = "Action blocked by compliance policy."
                    self.state = OrchestratorState.END
                elif decision == "require_approval":
                    self.state = OrchestratorState.APPROVAL
                else:
                    self.state = OrchestratorState.EXECUTE
                
        elif self.state == OrchestratorState.APPROVAL:
            approved = ApprovalGate.check_approval(self.tool_def.name, self.tool_args, self.current_risk)
            # In a real app we would get the actual authenticated user
            approval_tracker.record(self.tool_def.name, self.tool_args, "admin", approved)
            audit_logger.log_event("APPROVAL_DECISION", {"approved": approved})
            
            if approved:
                self.state = OrchestratorState.EXECUTE
            else:
                self.final_report = "Action denied by user."
                self.state = OrchestratorState.END
                
        elif self.state == OrchestratorState.EXECUTE:
            with tracer.start_as_current_span("tool_execute", {"tool": self.tool_def.name}):
                self.exec_result = self.tool_def.executor(self.tool_args)
                
            audit_logger.log_event("EXECUTE_COMPLETE", {"success": self.exec_result.success})
            self.state = OrchestratorState.VERIFY
            
        elif self.state == OrchestratorState.VERIFY:
            with tracer.start_as_current_span("verification"):
                # Phase 2: Simple verification (just checking success flag)
                if self.exec_result.success:
                    self.state = OrchestratorState.REPORT
                else:
                    self.final_report = f"Execution Failed: {self.exec_result.error}"
                    self.state = OrchestratorState.END
                
        elif self.state == OrchestratorState.REPORT:
            self.final_report = self.exec_result.output
            self.state = OrchestratorState.END
