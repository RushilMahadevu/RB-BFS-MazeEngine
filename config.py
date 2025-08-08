"""
Configuration management for the maze system.
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from visualization import ColorScheme


class MazeConfig:
    """Configuration manager for the maze system."""
    
    DEFAULT_CONFIG = {
        "visualization": {
            "theme": "classic",
            "use_unicode": False,
            "animation_speed": 0.1
        },
        "generation": {
            "default_algorithm": "iterative",
            "max_recursion_depth": 10000,
            "default_size": [21, 21]
        },
        "pathfinding": {
            "default_algorithm": "bfs",
            "show_statistics": True
        },
        "export": {
            "default_format": "txt",
            "include_solution": True,
            "default_directory": "exports"
        },
        "gui": {
            "window_size": [800, 600],
            "canvas_size": [400, 400],
            "max_cell_size": 20
        },
        "performance": {
            "warn_large_maze": 10000,
            "max_maze_area": 40000,
            "threading_enabled": True
        }
    }
    
    def __init__(self, config_file: str = "maze_config.json"):
        self.config_file = Path(config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
                print(f"{ColorScheme.GREEN}✅ Configuration loaded from {self.config_file}{ColorScheme.RESET}")
            except Exception as e:
                print(f"{ColorScheme.YELLOW}⚠️  Warning: Could not load config file: {e}{ColorScheme.RESET}")
                print(f"{ColorScheme.YELLOW}Using default configuration{ColorScheme.RESET}")
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"{ColorScheme.GREEN}✅ Configuration saved to {self.config_file}{ColorScheme.RESET}")
        except Exception as e:
            print(f"{ColorScheme.RED}❌ Error saving config: {e}{ColorScheme.RESET}")
    
    def _merge_config(self, file_config: Dict[str, Any]) -> None:
        """Merge file configuration with defaults."""
        for section, values in file_config.items():
            if section in self.config and isinstance(values, dict):
                self.config[section].update(values)
            else:
                self.config[section] = values
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        return self.config.get(section, {})
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        print(f"{ColorScheme.YELLOW}🔄 Configuration reset to defaults{ColorScheme.RESET}")
    
    def export_config(self, filename: str) -> None:
        """Export current configuration to a file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"{ColorScheme.GREEN}✅ Configuration exported to {filename}{ColorScheme.RESET}")
        except Exception as e:
            print(f"{ColorScheme.RED}❌ Error exporting config: {e}{ColorScheme.RESET}")
    
    def import_config(self, filename: str) -> None:
        """Import configuration from a file."""
        try:
            with open(filename, 'r') as f:
                imported_config = json.load(f)
                self._merge_config(imported_config)
            print(f"{ColorScheme.GREEN}✅ Configuration imported from {filename}{ColorScheme.RESET}")
        except Exception as e:
            print(f"{ColorScheme.RED}❌ Error importing config: {e}{ColorScheme.RESET}")
    
    def print_config(self) -> None:
        """Print current configuration."""
        print(f"\n{ColorScheme.BRIGHT_CYAN}📋 Current Configuration{ColorScheme.RESET}")
        print(f"{ColorScheme.CYAN}{'=' * 40}{ColorScheme.RESET}")
        
        for section, values in self.config.items():
            print(f"\n{ColorScheme.BRIGHT_YELLOW}[{section}]{ColorScheme.RESET}")
            for key, value in values.items():
                print(f"  {key}: {value}")
    
    def validate_config(self) -> bool:
        """Validate configuration values."""
        errors = []
        
        # Validate visualization settings
        theme = self.get("visualization", "theme")
        if theme not in ["classic", "dark", "neon"]:
            errors.append(f"Invalid theme: {theme}")
        
        # Validate generation settings
        max_depth = self.get("generation", "max_recursion_depth")
        if not isinstance(max_depth, int) or max_depth < 1000:
            errors.append(f"Invalid max_recursion_depth: {max_depth}")
        
        default_size = self.get("generation", "default_size")
        if not isinstance(default_size, list) or len(default_size) != 2:
            errors.append(f"Invalid default_size: {default_size}")
        
        # Validate performance settings
        warn_size = self.get("performance", "warn_large_maze")
        max_area = self.get("performance", "max_maze_area")
        if warn_size >= max_area:
            errors.append("warn_large_maze should be less than max_maze_area")
        
        if errors:
            print(f"{ColorScheme.RED}❌ Configuration validation errors:{ColorScheme.RESET}")
            for error in errors:
                print(f"  • {error}")
            return False
        
        print(f"{ColorScheme.GREEN}✅ Configuration is valid{ColorScheme.RESET}")
        return True


# Global configuration instance
config = MazeConfig()


def get_config() -> MazeConfig:
    """Get the global configuration instance."""
    return config
