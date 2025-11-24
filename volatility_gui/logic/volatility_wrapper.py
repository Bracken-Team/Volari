import os
import logging
from typing import Dict, Any, List

from volatility3 import framework
from volatility3.framework import contexts, automagic, plugins, interfaces, constants
from volatility3.framework.configuration import requirements
from volatility3.plugins.windows import pslist

# Configure logging to avoid spam
logging.basicConfig(level=logging.INFO)
vollog = logging.getLogger(__name__)

class VolatilityWrapper:
    def __init__(self):
        self.ctx = contexts.Context()
        self.failures = framework.import_files(framework.plugins, True)
        if self.failures:
            vollog.warning(f"Failed to import some plugins: {self.failures}")
            
        self.automagics = automagic.available(self.ctx)

    def run_plugin(self, plugin_name: str, file_path: str, additional_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Runs a specific plugin on a memory dump.
        
        Args:
            plugin_name: The name of the plugin to run (e.g., 'windows.pslist.PsList').
            file_path: Path to the memory dump file.
            additional_config: Optional dictionary of additional configuration parameters.
            
        Returns:
            A list of dictionaries representing the rows of the result.
        """
        # Reset context for clean run (optional, but good for isolation)
        # For now, we reuse context but ensure config is set correctly
        
        # Set the single location (memory dump file)
        single_location = f"file://{os.path.abspath(file_path)}"
        self.ctx.config["automagic.LayerStacker.single_location"] = single_location
        
        # Find the plugin class
        plugin_list = framework.list_plugins()
        if plugin_name not in plugin_list:
            raise ValueError(f"Plugin {plugin_name} not found.")
            
        plugin_class = plugin_list[plugin_name]
        
        # Run automagic to stack layers
        # We need to pass the plugin class to choose_automagic
        automagics = automagic.choose_automagic(self.automagics, plugin_class)
        
        # Construct the plugin
        # We need to populate the config with any requirements
        # For simple plugins like pslist, defaults might work, but we should handle config
        
        base_config_path = "plugins"
        plugin_config_path = interfaces.configuration.path_join(base_config_path, plugin_class.__name__)
        
        # Apply additional config if provided
        if additional_config:
            for key, value in additional_config.items():
                extended_path = interfaces.configuration.path_join(plugin_config_path, key)
                self.ctx.config[extended_path] = value

        # Construct the plugin instance
        try:
            plugin = plugins.construct_plugin(
                self.ctx,
                automagics,
                plugin_class,
                base_config_path,
                None, # Progress callback
                None  # File handler factory
            )
            
            # Run the plugin
            treegrid = plugin.run()
            
            # Convert TreeGrid to list of dicts
            return self._process_treegrid(treegrid)
            
        except Exception as e:
            vollog.error(f"Error running plugin {plugin_name}: {e}")
            raise e

    def _process_treegrid(self, treegrid: interfaces.renderers.TreeGrid) -> List[Dict[str, Any]]:
        """Converts a TreeGrid to a list of dictionaries."""
        results = []
        
        # Get column names
        columns = [col.name for col in treegrid.columns]
        
        def visitor(node, accumulator):
            row = {}
            for i, value in enumerate(node.values):
                # Handle different value types if necessary
                # For now, convert to string representation or keep as is
                # Volatility values can be complex objects
                row[columns[i]] = str(value) 
            accumulator.append(row)

        treegrid.populate(visitor, results)
        return results

    def get_available_plugins(self):
        return list(framework.list_plugins().keys())
