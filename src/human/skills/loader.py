import os
import yaml
from pathlib import Path
from human.tools.registry import registry, ToolDef
from human.safety.risk_classifier import RiskTier
from human.mcp.broker import MCPBroker
from human.observability.tracing import tracer
from typing import Dict, Any
from human.orchestrator.types import ExecutionResult

def _create_skill_executor(script_path: Path):
    """Creates an executor function that runs the skill script via MCP."""
    def executor(args: Dict[str, Any]) -> ExecutionResult:
        # For Phase 2, we just run the script with basic arg passing.
        # Ideally args are mapped to script flags.
        cmd = f"powershell.exe -File {script_path}"
        for k, v in args.items():
            cmd += f" -{k} '{v}'"
        return MCPBroker.execute_system_command(cmd)
    return executor

class SkillLoader:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(os.getcwd()) / skills_dir
        
    def load_all(self):
        """Scans the skills directory and registers them as tools."""
        if not self.skills_dir.exists():
            return
            
        with tracer.start_as_current_span("load_skills"):
            for skill_path in self.skills_dir.iterdir():
                if skill_path.is_dir():
                    self._load_skill(skill_path)

    def _load_skill(self, skill_dir: Path):
        meta_file = skill_dir / "skill.md"
        if not meta_file.exists():
            return
            
        # Very basic markdown frontmatter parser
        with open(meta_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        try:
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    
                    # Look for executable script
                    script_path = None
                    for ext in [".ps1", ".py", ".sh", ".bat"]:
                        potential_script = skill_dir / f"run{ext}"
                        if potential_script.exists():
                            script_path = potential_script
                            break
                            
                    if not script_path:
                        # Fallback to any ps1 file
                        scripts = list(skill_dir.glob("*.ps1"))
                        if scripts:
                            script_path = scripts[0]
                            
                    if script_path and metadata.get("name"):
                        risk_str = metadata.get("risk_tier", "READ_ONLY").upper()
                        risk_tier = RiskTier[risk_str] if hasattr(RiskTier, risk_str) else RiskTier.MUTATING_UNSCOPED
                        
                        tool = ToolDef(
                            name=metadata["name"],
                            description=metadata.get("description", ""),
                            risk_tier=risk_tier,
                            parameters_schema=metadata.get("parameters", {"type": "object", "properties": {}}),
                            executor=_create_skill_executor(script_path)
                        )
                        registry.register(tool)
        except Exception as e:
            # Silently ignore bad skills for now, let OTel trace it
            pass

loader = SkillLoader()
