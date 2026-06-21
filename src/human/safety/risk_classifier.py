from enum import Enum

class RiskTier(Enum):
    READ_ONLY = 0
    MUTATING_SCOPED = 1
    MUTATING_UNSCOPED = 2
    DESTRUCTIVE = 3

def requires_approval(tier: RiskTier) -> bool:
    """Determines if a given risk tier requires explicit human approval."""
    return tier in (RiskTier.MUTATING_UNSCOPED, RiskTier.DESTRUCTIVE)

def requires_notification(tier: RiskTier) -> bool:
    """Determines if a given risk tier requires notifying the user without blocking."""
    return tier == RiskTier.MUTATING_SCOPED
