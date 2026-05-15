import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any


class ConfigManager:
    """Manages Claw Code configuration files."""

    def __init__(self):
        self.claw_dir = Path.home() / ".claw"
        self.settings_path = self.claw_dir / "settings.json"
        self.workspace_config = self._find_workspace_config()

    def _find_workspace_config(self) -> Optional[Path]:
        """Find claw.json in current working directory or parents."""
        cwd = Path.cwd()
        for path in [cwd, cwd.parent, cwd.parent.parent]:
            config = path / "claw.json"
            if config.exists():
                return config
        return None

    def get_settings(self) -> Dict[str, Any]:
        """Read settings.json from .claw directory."""
        if not self.settings_path.exists():
            return {"model": "unknown", "sandbox": {"enabled": True}}

        try:
            with open(self.settings_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"model": "unknown", "sandbox": {"enabled": True}}

    def get_workspace_config(self) -> Dict[str, Any]:
        """Read claw.json from workspace."""
        if not self.workspace_config or not self.workspace_config.exists():
            return {"model": "claude-sonnet-4-20250514", "system_prompt": "You are a helpful coding assistant."}

        try:
            with open(self.workspace_config) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"model": "claude-sonnet-4-20250514", "system_prompt": "You are a helpful coding assistant."}

    def get_current_model(self) -> str:
        """Get current model from settings."""
        settings = self.get_settings()
        return settings.get("model", "unknown")

    def get_workspace_model(self) -> str:
        """Get model from workspace config."""
        config = self.get_workspace_config()
        return config.get("model", "claude-sonnet-4-20250514")

    def get_system_prompt(self) -> str:
        """Get system prompt from workspace config."""
        config = self.get_workspace_config()
        return config.get("system_prompt", "You are a helpful coding assistant.")

    def get_sandbox_enabled(self) -> bool:
        """Check if sandbox is enabled."""
        settings = self.get_settings()
        sandbox = settings.get("sandbox", {})
        return sandbox.get("enabled", True)


config_manager = ConfigManager()