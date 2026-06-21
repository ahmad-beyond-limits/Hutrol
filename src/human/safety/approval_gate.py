from rich.console import Console
from rich.prompt import Confirm
from human.safety.risk_classifier import RiskTier, requires_approval, requires_notification
from human.config.loader import load_config

console = Console()

class ApprovalGate:
    """Handles human-in-the-loop approvals for mutating actions."""
    
    @staticmethod
    def check_approval(tool_name: str, args: dict, risk_tier: RiskTier) -> bool:
        config = load_config()
        if config.get("SAFETY", "true").lower() == "false":
            console.print(f"[bold yellow]Notice:[/bold yellow] Auto-approving '{tool_name}' (SAFETY is disabled).")
            return True

        if risk_tier == RiskTier.READ_ONLY:
            return True
            
        if requires_notification(risk_tier):
            console.print(f"[bold yellow]Notice:[/bold yellow] Executing scoped mutating action '{tool_name}'.")
            return True
            
        if requires_approval(risk_tier):
            console.print(f"\n[bold red]WARNING:[/bold red] The agent has proposed a high-risk action ([bold]{risk_tier.name}[/bold]).")
            console.print(f"Tool: [bold cyan]{tool_name}[/bold cyan]")
            console.print(f"Arguments: {args}\n")
            
            # Use Rich's Confirm prompt to pause execution
            approved = Confirm.ask("Do you approve this action?")
            return approved
            
        return False
