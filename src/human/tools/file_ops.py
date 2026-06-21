import os
import glob
from typing import Dict, Any
from human.safety.risk_classifier import RiskTier
from human.orchestrator.types import ExecutionResult
from human.tools.registry import ToolDef, registry

def execute_find_files(args: Dict[str, Any]) -> ExecutionResult:
    pattern = args.get("pattern", "*")
    directory = args.get("directory", ".")
    
    try:
        search_path = os.path.join(directory, pattern)
        files = glob.glob(search_path, recursive=True)
        return ExecutionResult(
            success=True,
            output=f"Found {len(files)} files matching '{pattern}' in '{directory}':\n" + "\n".join(files)
        )
    except Exception as e:
        return ExecutionResult(success=False, output="", error=str(e))

find_files_tool = ToolDef(
    name="find_files",
    description="Find files matching a glob pattern.",
    risk_tier=RiskTier.READ_ONLY,
    parameters_schema={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Glob pattern (e.g. *.pdf, **/*.txt)"
            },
            "directory": {
                "type": "string",
                "description": "Directory to search in. Default is current directory."
            }
        },
        "required": ["pattern"]
    },
    executor=execute_find_files
)

# Register the tool
registry.register(find_files_tool)
