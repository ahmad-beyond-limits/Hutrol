import json
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class ConfigError(Exception):
    pass

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".human"
        self.config_file = self.config_dir / "config.json"
        self._ensure_exists()
        
    def _ensure_exists(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            # Default empty config
            self.save_config({
                "PROVIDER": "openrouter",
                "OPENROUTER_MODEL": "meta-llama/llama-3.1-8b-instruct",
                "OLLAMA_MODEL": "llama3",
                "OLLAMA_HOST": "http://localhost:11434"
            })
            
    def load_config(self) -> Dict[str, Any]:
        with open(self.config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        # Fall back to .env variables so existing setups don't break
        load_dotenv()
        
        if not config.get("OPENROUTER_API_KEY") and os.getenv("OPENROUTER_API_KEY"):
            config["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
        if not config.get("OPENROUTER_MODEL") and os.getenv("OPENROUTER_MODEL"):
            config["OPENROUTER_MODEL"] = os.getenv("OPENROUTER_MODEL")
            
        return config
            
    def save_config(self, config: Dict[str, Any]):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
            
    def set_key(self, key: str, value: str):
        config = self.load_config()
        config[key] = value
        self.save_config(config)

config_manager = ConfigManager()

def load_config() -> Dict[str, Any]:
    config = config_manager.load_config()
    provider = config.get("PROVIDER", "openrouter")
    
    if provider == "openrouter":
        if not config.get("OPENROUTER_API_KEY"):
            raise ConfigError("Model not setup! Please add an OpenRouter API key using:\n  hutrol config set OPENROUTER_API_KEY <your-key>\nOr switch to local Ollama using:\n  hutrol config set PROVIDER ollama")
        if not config.get("OPENROUTER_MODEL"):
            raise ConfigError("Model not setup! Please set OPENROUTER_MODEL using:\n  hutrol config set OPENROUTER_MODEL <model-name>")
            
    elif provider == "ollama":
        if not config.get("OLLAMA_HOST") or not config.get("OLLAMA_MODEL"):
            raise ConfigError("Model not setup! Please set OLLAMA_HOST and OLLAMA_MODEL using:\n  hutrol config set OLLAMA_MODEL <model-name>")
    else:
        raise ConfigError(f"Unknown provider: {provider}")
        
    return config
