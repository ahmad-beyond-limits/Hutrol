import sys
import typer
from rich.console import Console
from human.config.loader import load_config, ConfigError, config_manager
from human.providers.openrouter_provider import OpenRouterProvider
from human.providers.ollama_provider import OllamaProvider
from human.orchestrator.harness import Harness

app = typer.Typer(help="Hutrol CLI — Enterprise Agentic Harness Platform")
console = Console()

@app.command()
def run(prompt: str):
    """Execute a single command via the Agentic Harness."""
    try:
        # Load configuration
        config = load_config()
        
        # Initialize Provider
        provider_name = config.get("PROVIDER", "openrouter")
        if provider_name == "openrouter":
            provider = OpenRouterProvider(
                api_key=config["OPENROUTER_API_KEY"],
                model=config["OPENROUTER_MODEL"]
            )
        else:
            provider = OllamaProvider(
                host=config.get("OLLAMA_HOST", "http://localhost:11434"),
                model=config.get("OLLAMA_MODEL", "llama3")
            )
        
        # Initialize Harness
        harness = Harness(provider=provider)
        
        # Execute prompt
        console.print(f"[bold blue]User Request:[/bold blue] {prompt}")
        result = harness.execute(prompt)
        console.print(f"\n[bold green]Result:[/bold green]\n{result}")
        
    except ConfigError as ce:
        console.print(f"[bold yellow]{ce}[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def repl():
    """Start an interactive REPL session."""
    console.print("[bold green]Hutrol CLI Started. Type 'exit' or 'quit' to leave.[/bold green]")
    
    try:
        config = load_config()
        provider_name = config.get("PROVIDER", "openrouter")
        if provider_name == "openrouter":
            provider = OpenRouterProvider(
                api_key=config["OPENROUTER_API_KEY"],
                model=config["OPENROUTER_MODEL"]
            )
        else:
            provider = OllamaProvider(
                host=config.get("OLLAMA_HOST", "http://localhost:11434"),
                model=config.get("OLLAMA_MODEL", "llama3")
            )
        harness = Harness(provider=provider)
        
        while True:
            prompt = console.input("[bold blue]hutrol>[/bold blue] ")
            if prompt.lower() in ("exit", "quit"):
                break
            if not prompt.strip():
                continue
                
            result = harness.execute(prompt)
            console.print(f"[bold green]Result:[/bold green]\n{result}")
            
    except ConfigError as ce:
        console.print(f"[bold yellow]{ce}[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

config_app = typer.Typer(help="Manage Hutrol settings.")
app.add_typer(config_app, name="config")

@config_app.command("set")
def config_set(key: str, value: str):
    """Set a configuration value."""
    config_manager.set_key(key, value)
    console.print(f"[bold green]Successfully set {key} to {value}.[/bold green]")

@config_app.command("list")
def config_list():
    """List all current configurations."""
    config = config_manager.load_config()
    for k, v in config.items():
        if ("API_KEY" in k or "TOKEN" in k) and v:
            # Show first 4 characters, mask the rest
            masked = v[:4] + "*" * (len(v) - 4) if len(v) > 4 else "*" * len(v)
            console.print(f"[bold cyan]{k}[/bold cyan]: {masked}")
        else:
            console.print(f"[bold cyan]{k}[/bold cyan]: {v}")

rule_app = typer.Typer(help="Manage command safety rules.")
app.add_typer(rule_app, name="rule")

@rule_app.command("set")
def rule_set(color: str, command: str):
    """Set the safety color for a command (red, yellow, green)."""
    if color.lower() not in ["red", "yellow", "green"]:
        console.print("[bold red]Error:[/bold red] Color must be one of: red, yellow, green.")
        raise typer.Exit(1)
        
    config_manager.set_rule(command, color)
    console.print(f"[bold green]Successfully set '{command}' to {color}.[/bold green]")

@app.command()
def update():
    """Update Hutrol to the latest version via Windows Installer (OTA)."""
    import urllib.request
    import json
    import os
    import subprocess
    import ssl
    import shutil
    from pathlib import Path
    
    console.print("[bold yellow]Checking for latest updates from GitHub...[/bold yellow]")
    
    # Bypass PyInstaller SSL certificate issues on Windows
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    api_url = "https://api.github.com/repos/ahmad-beyond-limits/Hutrol/releases/latest"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Hutrol-CLI'})
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            
        assets = data.get("assets", [])
        installer_url = None
        for asset in assets:
            if asset.get("name") == "HutrolSetup.exe":
                installer_url = asset.get("browser_download_url")
                break
                
        if not installer_url:
            console.print("[bold red]Error:[/bold red] No installer (HutrolSetup.exe) found in the latest release.")
            raise typer.Exit(1)
            
        temp_dir = Path(os.environ.get("TEMP", "."))
        installer_path = temp_dir / "HutrolSetup_update.exe"
        
        console.print(f"[bold yellow]Downloading latest release ({data.get('tag_name')})...[/bold yellow]")
        
        dl_req = urllib.request.Request(installer_url, headers={'User-Agent': 'Hutrol-CLI'})
        with urllib.request.urlopen(dl_req, context=ctx) as response, open(installer_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        
        console.print("[bold green]Download complete! Launching silent installer...[/bold green]")
        
        # Launch installer in the background completely silently, closing the current app.
        subprocess.Popen(
            [str(installer_path), "/SILENT", "/SP-", "/SUPPRESSMSGBOXES", "/FORCECLOSEAPPLICATIONS"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Terminate the current CLI so the installer can overwrite the executable
        sys.exit(0)
        
    except Exception as e:
        console.print(f"[bold red]Update failed:[/bold red] {e}")

@app.command()
def export_audit():
    """Export compliance logs as a zipped archive."""
    import zipfile
    from pathlib import Path
    import hashlib
    import time
    
    audit_dir = Path.home() / ".human"
    export_file = Path.cwd() / f"human_compliance_export_{int(time.time())}.zip"
    
    console.print("[bold yellow]Generating compliance export...[/bold yellow]")
    
    try:
        with zipfile.ZipFile(export_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_name in ["audit.jsonl", "trace.jsonl", "approvals.jsonl"]:
                file_path = audit_dir / file_name
                if file_path.exists():
                    zipf.write(file_path, arcname=file_name)
                    
        # Generate simple checksum
        sha256 = hashlib.sha256()
        with open(export_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
                
        checksum = sha256.hexdigest()
        console.print(f"[bold green]Export created:[/bold green] {export_file}")
        console.print(f"[bold cyan]SHA-256 Checksum:[/bold cyan] {checksum}")
        
    except Exception as e:
        console.print(f"[bold red]Failed to export audit logs:[/bold red] {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("repl")
    app()
