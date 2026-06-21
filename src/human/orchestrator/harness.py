from human.providers.base import LLMProvider
from human.orchestrator.state_machine import StateMachine
import human.tools  # Trigger tool registration

class Harness:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.state_machine = StateMachine(provider)

    def execute(self, prompt: str) -> str:
        """Runs the orchestrator state machine for a single prompt."""
        return self.state_machine.run(prompt)
