import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal


class SettingsManager(QObject):
    """Centralized settings management with JSON persistence."""
    
    # Signals
    setting_changed = pyqtSignal(str, object)  # setting_path, new_value
    
    # Default settings structure
    DEFAULT_SETTINGS = {
        "application": {
            "theme": "dark",
            "auto_save": True,
            "default_export_format": "csv",
            "max_concurrent_tasks": 1
        },
        "virustotal": {
            "api_key": "",
            "cache_enabled": True,
            "rate_limit": 4
        },
        "volatility": {
            "symbol_path": "",
            "plugin_paths": [],
            "cache_dir": str(Path.home() / ".volatility3" / "cache"),
            "isf_path": ""
        },
        "report": {
            "analyst_name": "",
            "company": "",
            "logo_path": "",
            "template": "default"
        },
        "performance": {
            "memory_limit_mb": 4096,
            "worker_threads": 4,
            "cache_size_mb": 512
        },
        "advanced": {
            "debug_mode": False,
            "auto_investigation_plugins": [
                "windows.info.Info",
                "windows.pslist.PsList",
                "windows.netscan.NetScan",
                "windows.filescan.FileScan"
            ],
            "plugin_timeout_seconds": 300
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize settings manager.
        
        Args:
            config_path: Path to config file. Defaults to ~/.volatility_gui/config.json
        """
        super().__init__()
        
        if config_path is None:
            config_dir = self._get_config_dir()
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.json"
        else:
            self.config_path = Path(config_path)
            
        self.settings: Dict[str, Any] = {}
        self.load()
    
    def _get_config_dir(self) -> Path:
        """Get platform-appropriate config directory."""
        if sys.platform == "darwin":
            # macOS: ~/Library/Application Support/Volari
            return Path.home() / "Library" / "Application Support" / "Volari"
        elif sys.platform == "win32":
            # Windows: %APPDATA%/Volari
            appdata = os.environ.get('APPDATA', Path.home())
            return Path(appdata) / "Volari"
        else:
            # Linux/Unix: ~/.config/volari
            xdg_config = os.environ.get('XDG_CONFIG_HOME', Path.home() / ".config")
            return Path(xdg_config) / "volari"
        
    def load(self):
        """Load settings from disk, creating defaults if file doesn't exist."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_settings = json.load(f)
                    
                # Merge with defaults to ensure all keys exist
                self.settings = self._merge_with_defaults(loaded_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = self.DEFAULT_SETTINGS.copy()
        else:
            self.settings = self.DEFAULT_SETTINGS.copy()
            self.save()
            
    def save(self):
        """Save settings to disk."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def _merge_with_defaults(self, loaded: Dict) -> Dict:
        """Merge loaded settings with defaults to ensure all keys exist."""
        result = self.DEFAULT_SETTINGS.copy()
        
        for category, values in loaded.items():
            if category in result and isinstance(values, dict):
                result[category].update(values)
            else:
                result[category] = values
                
        return result
        
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation.
        
        Args:
            path: Setting path (e.g., "application.theme")
            default: Default value if setting doesn't exist
            
        Returns:
            Setting value or default
        """
        parts = path.split('.')
        value = self.settings
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
                
        return value
        
    def set(self, path: str, value: Any, save: bool = True):
        """
        Set a setting value using dot notation.
        
        Args:
            path: Setting path (e.g., "application.theme")
            value: New value
            save: Whether to save to disk immediately
        """
        parts = path.split('.')
        
        # Navigate to the parent dict
        current = self.settings
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
            
        # Set the value
        old_value = current.get(parts[-1])
        current[parts[-1]] = value
        
        # Validate critical settings
        if not self._validate_setting(path, value):
            # Revert if validation fails
            current[parts[-1]] = old_value
            return False
            
        # Emit signal
        self.setting_changed.emit(path, value)
        
        # Save if requested
        if save:
            self.save()
            
        return True
        
    def _validate_setting(self, path: str, value: Any) -> bool:
        """Validate setting values."""
        # Validate max_concurrent_tasks
        if path == "application.max_concurrent_tasks":
            if not isinstance(value, int) or value < 1 or value > 10:
                print(f"Invalid max_concurrent_tasks: {value}. Must be 1-10.")
                return False
                
        # Validate rate_limit
        if path == "virustotal.rate_limit":
            if not isinstance(value, int) or value < 1 or value > 1000:
                print(f"Invalid rate_limit: {value}. Must be 1-1000.")
                return False
                
        # Validate memory_limit_mb
        if path == "performance.memory_limit_mb":
            if not isinstance(value, int) or value < 512:
                print(f"Invalid memory_limit_mb: {value}. Must be >= 512.")
                return False
                
        # Validate worker_threads
        if path == "performance.worker_threads":
            if not isinstance(value, int) or value < 1 or value > 16:
                print(f"Invalid worker_threads: {value}. Must be 1-16.")
                return False
                
        # Validate timeout
        if path == "advanced.plugin_timeout_seconds":
            if not isinstance(value, int) or value < 10:
                print(f"Invalid plugin_timeout_seconds: {value}. Must be >= 10.")
                return False
                
        return True
        
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save()
        self.setting_changed.emit("*", None)  # Signal global reset
        
    def reset_category(self, category: str):
        """Reset a specific category to defaults."""
        if category in self.DEFAULT_SETTINGS:
            self.settings[category] = self.DEFAULT_SETTINGS[category].copy()
            self.save()
            self.setting_changed.emit(f"{category}.*", None)
            
    # Convenience methods for common settings
    def get_theme(self) -> str:
        return self.get("application.theme", "light")
        
    def set_theme(self, theme: str):
        self.set("application.theme", theme)
        
    def get_max_concurrent_tasks(self) -> int:
        return self.get("application.max_concurrent_tasks", 1)
        
    def set_max_concurrent_tasks(self, count: int):
        self.set("application.max_concurrent_tasks", count)
        
    def get_vt_api_key(self) -> str:
        return self.get("virustotal.api_key", "")
        
    def set_vt_api_key(self, key: str):
        self.set("virustotal.api_key", key)
        
    def get_analyst_name(self) -> str:
        return self.get("report.analyst_name", "")
        
    def set_analyst_name(self, name: str):
        self.set("report.analyst_name", name)
        
    def get_company(self) -> str:
        return self.get("report.company", "")
        
    def set_company(self, company: str):
        self.set("report.company", company)
        
    def get_auto_investigation_plugins(self) -> List[str]:
        return self.get("advanced.auto_investigation_plugins", [])
        
    def set_auto_investigation_plugins(self, plugins: List[str]):
        self.set("advanced.auto_investigation_plugins", plugins)
