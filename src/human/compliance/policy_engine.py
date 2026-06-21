from typing import Dict, Any
from human.safety.risk_classifier import RiskTier

class PolicyEngine:
    """Deterministic governance layer for evaluating tool calls."""
    
    def __init__(self):
        # In a real enterprise, these would be loaded from a policy.json
        self.allowed_tools = ["list_directory", "read_file", "search_web", "delegate_task"]
        self.approval_tools = ["write_file", "run_system_command"]
        self.blocked_tools = []
        
        # Policy rules by user role (mocked to 'admin' for now)
        self.current_role = "admin"

    def evaluate(self, tool_name: str, args: Dict[str, Any], computed_risk: RiskTier) -> str:
        """Returns 'allow', 'require_approval', or 'block'."""
        
        # 1. Check explicit tool policies
        if tool_name in self.blocked_tools:
            return "block"
            
        if tool_name in self.allowed_tools:
            # Check if risk overrides allow list (e.g., trying to read /etc/shadow)
            if computed_risk == RiskTier.DESTRUCTIVE:
                return "block"
            if computed_risk == RiskTier.MUTATING_UNSCOPED:
                return "require_approval"
            return "allow"
            
        # 2. Check risk-based policies
        if computed_risk == RiskTier.READ_ONLY:
            return "allow"
            
        if computed_risk in [RiskTier.MUTATING_SCOPED, RiskTier.MUTATING_UNSCOPED]:
            return "require_approval"
            
        if computed_risk == RiskTier.DESTRUCTIVE:
            if self.current_role == "admin":
                return "require_approval"
            return "block"
            
        # Default fallback is always require approval for safety
        return "require_approval"

policy_engine = PolicyEngine()
