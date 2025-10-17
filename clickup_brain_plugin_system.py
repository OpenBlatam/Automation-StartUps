#!/usr/bin/env python3
"""
ClickUp Brain Plugin System
==========================

Extensible plugin architecture for adding new functionality.
"""

import sys
import importlib
import importlib.util
import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import threading
from contextlib import contextmanager

ROOT = Path(__file__).parent
PLUGINS_DIR = ROOT / "plugins"

@dataclass
class PluginInfo:
    """Plugin metadata and information."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    enabled: bool = True
    loaded_at: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None

class PluginBase(ABC):
    """Base class for all plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")
        self._enabled = True
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass
    
    @property
    @abstractmethod
    def author(self) -> str:
        """Plugin author."""
        pass
    
    def get_dependencies(self) -> List[str]:
        """Get plugin dependencies."""
        return []
    
    def get_hooks(self) -> List[str]:
        """Get available hooks."""
        return []
    
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """Get configuration schema."""
        return None
    
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        try:
            self.logger.info(f"Initializing plugin {self.name}")
            return self._on_initialize()
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin {self.name}: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        try:
            self.logger.info(f"Cleaning up plugin {self.name}")
            self._on_cleanup()
        except Exception as e:
            self.logger.error(f"Error during plugin cleanup {self.name}: {e}")
    
    def enable(self) -> None:
        """Enable the plugin."""
        self._enabled = True
        self._on_enable()
    
    def disable(self) -> None:
        """Disable the plugin."""
        self._enabled = False
        self._on_disable()
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        schema = self.get_config_schema()
        if not schema:
            return True
        
        try:
            return self._validate_config_schema(config, schema)
        except Exception as e:
            self.logger.error(f"Config validation failed for {self.name}: {e}")
            return False
    
    def _validate_config_schema(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate configuration against schema."""
        # Simple schema validation - can be extended with jsonschema
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in config:
                self.logger.error(f"Required field '{field}' missing in config")
                return False
        
        return True
    
    def _on_initialize(self) -> bool:
        """Override in subclasses for initialization logic."""
        return True
    
    def _on_cleanup(self) -> None:
        """Override in subclasses for cleanup logic."""
        pass
    
    def _on_enable(self) -> None:
        """Override in subclasses for enable logic."""
        pass
    
    def _on_disable(self) -> None:
        """Override in subclasses for disable logic."""
        pass

class HookManager:
    """Manages plugin hooks and event dispatching."""
    
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
    
    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a callback for a hook."""
        with self._lock:
            if hook_name not in self.hooks:
                self.hooks[hook_name] = []
            self.hooks[hook_name].append(callback)
    
    def unregister_hook(self, hook_name: str, callback: Callable) -> None:
        """Unregister a callback from a hook."""
        with self._lock:
            if hook_name in self.hooks:
                try:
                    self.hooks[hook_name].remove(callback)
                except ValueError:
                    pass
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger all callbacks for a hook."""
        results = []
        
        with self._lock:
            callbacks = self.hooks.get(hook_name, []).copy()
        
        for callback in callbacks:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logging.error(f"Error in hook {hook_name}: {e}")
        
        return results
    
    def get_hook_names(self) -> List[str]:
        """Get all registered hook names."""
        with self._lock:
            return list(self.hooks.keys())

class PluginManager:
    """Main plugin management system."""
    
    def __init__(self, plugins_dir: Path = PLUGINS_DIR):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.hook_manager = HookManager()
        self.logger = logging.getLogger("plugin_manager")
        self._lock = threading.Lock()
        
        # Create plugins directory if it doesn't exist
        self.plugins_dir.mkdir(exist_ok=True)
    
    def discover_plugins(self) -> List[Path]:
        """Discover available plugin files."""
        plugin_files = []
        
        for file_path in self.plugins_dir.glob("*.py"):
            if file_path.name != "__init__.py":
                plugin_files.append(file_path)
        
        return plugin_files
    
    def load_plugin(self, plugin_path: Path) -> bool:
        """Load a plugin from file."""
        try:
            # Import the plugin module
            spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)
            if not spec or not spec.loader:
                self.logger.error(f"Could not load plugin {plugin_path}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginBase) and 
                    obj != PluginBase):
                    plugin_classes.append(obj)
            
            if not plugin_classes:
                self.logger.warning(f"No plugin classes found in {plugin_path}")
                return False
            
            # Load each plugin class
            for plugin_class in plugin_classes:
                plugin_instance = plugin_class()
                plugin_name = plugin_instance.name
                
                if plugin_name in self.plugins:
                    self.logger.warning(f"Plugin {plugin_name} already loaded")
                    continue
                
                # Create plugin info
                plugin_info = PluginInfo(
                    name=plugin_name,
                    version=plugin_instance.version,
                    description=plugin_instance.description,
                    author=plugin_instance.author,
                    dependencies=plugin_instance.get_dependencies(),
                    hooks=plugin_instance.get_hooks(),
                    config_schema=plugin_instance.get_config_schema(),
                    loaded_at=datetime.now()
                )
                
                # Initialize plugin
                if plugin_instance.initialize():
                    with self._lock:
                        self.plugins[plugin_name] = plugin_instance
                        self.plugin_info[plugin_name] = plugin_info
                    
                    # Register hooks
                    self._register_plugin_hooks(plugin_instance)
                    
                    self.logger.info(f"Successfully loaded plugin {plugin_name}")
                else:
                    self.logger.error(f"Failed to initialize plugin {plugin_name}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_path}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        with self._lock:
            if plugin_name not in self.plugins:
                self.logger.warning(f"Plugin {plugin_name} not found")
                return False
            
            plugin = self.plugins[plugin_name]
            
            # Unregister hooks
            self._unregister_plugin_hooks(plugin)
            
            # Cleanup plugin
            plugin.cleanup()
            
            # Remove from registry
            del self.plugins[plugin_name]
            del self.plugin_info[plugin_name]
            
            self.logger.info(f"Successfully unloaded plugin {plugin_name}")
            return True
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin."""
        if plugin_name in self.plugins:
            self.unload_plugin(plugin_name)
        
        # Find and reload the plugin file
        plugin_files = self.discover_plugins()
        for plugin_file in plugin_files:
            if plugin_file.stem == plugin_name:
                return self.load_plugin(plugin_file)
        
        self.logger.error(f"Plugin file for {plugin_name} not found")
        return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        with self._lock:
            if plugin_name not in self.plugins:
                self.logger.warning(f"Plugin {plugin_name} not found")
                return False
            
            plugin = self.plugins[plugin_name]
            plugin.enable()
            self.plugin_info[plugin_name].enabled = True
            
            self.logger.info(f"Enabled plugin {plugin_name}")
            return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        with self._lock:
            if plugin_name not in self.plugins:
                self.logger.warning(f"Plugin {plugin_name} not found")
                return False
            
            plugin = self.plugins[plugin_name]
            plugin.disable()
            self.plugin_info[plugin_name].enabled = False
            
            self.logger.info(f"Disabled plugin {plugin_name}")
            return True
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get a plugin instance."""
        with self._lock:
            return self.plugins.get(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information."""
        with self._lock:
            return self.plugin_info.get(plugin_name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """List all loaded plugins."""
        with self._lock:
            return list(self.plugin_info.values())
    
    def load_all_plugins(self) -> int:
        """Load all discovered plugins."""
        plugin_files = self.discover_plugins()
        loaded_count = 0
        
        for plugin_file in plugin_files:
            if self.load_plugin(plugin_file):
                loaded_count += 1
        
        self.logger.info(f"Loaded {loaded_count} plugins")
        return loaded_count
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger a hook across all plugins."""
        return self.hook_manager.trigger_hook(hook_name, *args, **kwargs)
    
    def _register_plugin_hooks(self, plugin: PluginBase) -> None:
        """Register hooks for a plugin."""
        hooks = plugin.get_hooks()
        for hook_name in hooks:
            # Look for hook methods in the plugin
            hook_method = getattr(plugin, f"hook_{hook_name}", None)
            if hook_method and callable(hook_method):
                self.hook_manager.register_hook(hook_name, hook_method)
    
    def _unregister_plugin_hooks(self, plugin: PluginBase) -> None:
        """Unregister hooks for a plugin."""
        hooks = plugin.get_hooks()
        for hook_name in hooks:
            hook_method = getattr(plugin, f"hook_{hook_name}", None)
            if hook_method and callable(hook_method):
                self.hook_manager.unregister_hook(hook_name, hook_method)

# Global plugin manager instance
plugin_manager = PluginManager()

def load_plugin(plugin_path: Path) -> bool:
    """Load a plugin using the global manager."""
    return plugin_manager.load_plugin(plugin_path)

def unload_plugin(plugin_name: str) -> bool:
    """Unload a plugin using the global manager."""
    return plugin_manager.unload_plugin(plugin_name)

def get_plugin(plugin_name: str) -> Optional[PluginBase]:
    """Get a plugin using the global manager."""
    return plugin_manager.get_plugin(plugin_name)

def trigger_hook(hook_name: str, *args, **kwargs) -> List[Any]:
    """Trigger a hook using the global manager."""
    return plugin_manager.trigger_hook(hook_name, *args, **kwargs)

if __name__ == "__main__":
    # Demo plugin system
    print("ClickUp Brain Plugin System Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create a sample plugin
    sample_plugin_code = '''
from clickup_brain_plugin_system import PluginBase

class SamplePlugin(PluginBase):
    @property
    def name(self):
        return "sample_plugin"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "A sample plugin for demonstration"
    
    @property
    def author(self):
        return "ClickUp Brain Team"
    
    def get_hooks(self):
        return ["before_task_creation", "after_task_creation"]
    
    def hook_before_task_creation(self, task_data):
        print(f"Sample plugin: Before task creation - {task_data}")
        return task_data
    
    def hook_after_task_creation(self, task_id):
        print(f"Sample plugin: After task creation - {task_id}")
        return task_id
'''
    
    # Write sample plugin
    sample_plugin_path = PLUGINS_DIR / "sample_plugin.py"
    sample_plugin_path.write_text(sample_plugin_code)
    
    # Load all plugins
    loaded_count = plugin_manager.load_all_plugins()
    print(f"Loaded {loaded_count} plugins")
    
    # List plugins
    plugins = plugin_manager.list_plugins()
    for plugin_info in plugins:
        print(f"Plugin: {plugin_info.name} v{plugin_info.version} by {plugin_info.author}")
        print(f"  Description: {plugin_info.description}")
        print(f"  Hooks: {plugin_info.hooks}")
        print(f"  Enabled: {plugin_info.enabled}")
    
    # Test hooks
    print("\nTesting hooks:")
    results = plugin_manager.trigger_hook("before_task_creation", {"title": "Test Task"})
    print(f"Hook results: {results}")
    
    results = plugin_manager.trigger_hook("after_task_creation", "task_123")
    print(f"Hook results: {results}")
    
    # Test plugin management
    print("\nTesting plugin management:")
    plugin_manager.disable_plugin("sample_plugin")
    print("Plugin disabled")
    
    plugin_manager.enable_plugin("sample_plugin")
    print("Plugin enabled")
    
    # Cleanup
    plugin_manager.unload_plugin("sample_plugin")
    print("Plugin unloaded")
    
    # Remove sample plugin file
    sample_plugin_path.unlink()
    
    print("\nPlugin system demo completed!")









