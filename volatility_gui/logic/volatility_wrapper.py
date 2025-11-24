import os
import io
import logging
from typing import Dict, Any, List

from volatility3 import framework, plugins
from volatility3.framework import contexts, automagic, interfaces, constants, plugins as framework_plugins
from volatility3.framework.configuration import requirements
from volatility3.plugins.windows import pslist

# Configure logging to avoid spam
logging.basicConfig(level=logging.INFO)
vollog = logging.getLogger(__name__)

class VolatilityWrapper:
    def __init__(self):
        self.ctx = contexts.Context()
        self.failures = framework.import_files(plugins, True)
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
        # Reset context for clean run
        self.ctx = contexts.Context()
        
        # Re-initialize automagics with the new context
        self.automagics = automagic.available(self.ctx)
        
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
            plugin = framework_plugins.construct_plugin(
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
        
        # Access the internal generator that was passed to the TreeGrid
        # The generator yields (level, values) tuples
        try:
            if hasattr(treegrid, '_generator') and treegrid._generator is not None:
                for level, item in treegrid._generator:
                    row = {}
                    for i, value in enumerate(item):
                        try:
                            row[columns[i]] = str(value)
                        except Exception as e:
                            vollog.warning(f"Error converting value at index {i}: {e}")
                            row[columns[i]] = "N/A"
                    results.append(row)
            else:
                vollog.error("TreeGrid has no _generator attribute or it's None")
        except Exception as e:
            vollog.error(f"Error iterating TreeGrid: {e}")
            import traceback
            vollog.error(traceback.format_exc())
        
        vollog.info(f"Processed {len(results)} rows from TreeGrid")
        return results

    def dump_process(self, file_path: str, pid: str, output_dir: str) -> str:
        """
        Dump a process to disk using windows.dumpfiles plugin.
        
        Args:
            file_path: Path to the memory dump file
            pid: Process ID to dump
            output_dir: Directory to save the dumped process
            
        Returns:
            Path to the dumped directory
        """
        import os
        from volatility3.framework.interfaces import plugins as plugins_interface
        
        # Proper FileHandler implementation that inherits from FileHandlerInterface
        class FileHandler(plugins_interface.FileHandlerInterface):
            def __init__(self, filename: str):
                super().__init__(filename)
                self.output_dir = output_dir # output_dir is captured from the enclosing scope
                self.file_count = 0
                self._file_objects = []
            
            def _get_final_filename(self):
                """Gets the final filename in the output directory."""
                os.makedirs(self.output_dir, exist_ok=True)
                output_filename = os.path.join(self.output_dir, self.preferred_filename)
                filename_base, extension = os.path.splitext(output_filename)
                
                counter = 1
                while os.path.exists(output_filename):
                    output_filename = f"{filename_base}-{counter}{extension}"
                    counter += 1
                
                return output_filename
            
            def write(self, data):
                """Write data to the file."""
                if not hasattr(self, '_buffer'):
                    self._buffer = io.BytesIO()
                if hasattr(data, 'read'):
                    self._buffer.write(data.read())
                else:
                    self._buffer.write(data)
                return len(data) if not hasattr(data, 'read') else len(data.read())
            
            def close(self):
                """Close and save the file."""
                if self.closed:
                    return
                
                if hasattr(self, '_buffer'):
                    output_filename = self._get_final_filename()
                    with open(output_filename, 'wb') as f:
                        self._buffer.seek(0)
                        f.write(self._buffer.read())
                    self.file_count += 1
                    vollog.info(f"Saved file: {output_filename}")
                
                super().close()

        
        # Save current directory
        original_dir = os.getcwd()
        
        try:
            # Change to output directory so files are created there
            os.chdir(output_dir)
            
            # Reset context for clean run
            self.ctx = contexts.Context()
            
            # Re-initialize automagics with the new context
            self.automagics = automagic.available(self.ctx)
            
            # Set the single location (memory dump file)
            single_location = f"file://{os.path.abspath(file_path)}"
            self.ctx.config["automagic.LayerStacker.single_location"] = single_location
            
            # Use windows.dumpfiles plugin
            plugin_name = "windows.dumpfiles.DumpFiles"
            plugin_list = framework.list_plugins()
            plugin_class = plugin_list.get(plugin_name)
            
            if not plugin_class:
                raise ValueError(f"Plugin {plugin_name} not found")
            
            # Set up configuration for dumpfiles
            base_config_path = "plugins"
            # Filter by PID
            self.ctx.config[interfaces.configuration.path_join(base_config_path, plugin_name, "pid")] = [int(pid)]
            
            # Choose appropriate automagics
            automagics = automagic.choose_automagic(self.automagics, plugin_class)
            
            # Construct the plugin with FileHandler class (not instance)
            plugin = framework_plugins.construct_plugin(
                self.ctx,
                automagics,
                plugin_class,
                base_config_path,
                None,  # Progress callback
                FileHandler  # Pass the class, not an instance
            )
            
            # Run the plugin - this will create dump files in current directory
            treegrid = plugin.run()
            
            # Iterate through results to trigger file creation
            file_count = 0
            if hasattr(treegrid, '_generator') and treegrid._generator is not None:
                for level, item in treegrid._generator:
                    file_count += 1
            
            if file_count == 0:
                raise Exception(f"No files dumped for PID {pid}")
            
            vollog.info(f"Dumped {file_count} files for process {pid} to {output_dir}")
            return output_dir
            
        finally:
            # Restore original directory
            os.chdir(original_dir)

    def get_available_plugins(self):
        return list(framework.list_plugins().keys())
