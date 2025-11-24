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
        self.ctx = None
        self.automagics = []
        self.failures = framework.import_files(plugins, True)
        if self.failures:
            vollog.warning(f"Failed to import some plugins: {self.failures}")

    def load_file(self, file_path: str, **kwargs):
        """
        Load a memory dump file and initialize the context.
        
        Args:
            file_path: Path to the memory dump file.
            **kwargs: Additional arguments (e.g., progress_callback)
        """
        import os
        from volatility3.framework import contexts, automagic
        
        # Reset context for clean run
        self.ctx = contexts.Context()
        
        # Re-initialize automagics with the new context
        self.automagics = automagic.available(self.ctx)
        
        # Set the single location (memory dump file)
        single_location = f"file://{os.path.abspath(file_path)}"
        self.ctx.config["automagic.LayerStacker.single_location"] = single_location

    def run_plugin(self, plugin_name: str, additional_config: Dict[str, Any] = None, progress_callback=None) -> List[Dict[str, Any]]:
        """
        Run a specific Volatility 3 plugin.
        
        Args:
            plugin_name: The name of the plugin to run (e.g., "windows.pslist.PsList")
            additional_config: Optional dictionary of configuration options
            progress_callback: Optional callback function for progress reporting
            
        Returns:
            A list of dictionaries containing the plugin results
        """
        if not self.ctx:
            raise RuntimeError("Context not initialized. Load a file first.")
            
        import volatility3.framework.plugins as framework_plugins
        from volatility3.framework import automagic, interfaces
        
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
                progress_callback, # Progress callback
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
        # and delegates to a real file object
        class FileHandler(plugins_interface.FileHandlerInterface):
            def __init__(self, filename: str):
                super().__init__(filename)
                self.output_dir = output_dir # output_dir is captured from the enclosing scope
                
                # Determine final filename immediately
                os.makedirs(self.output_dir, exist_ok=True)
                output_filename = os.path.join(self.output_dir, self.preferred_filename)
                filename_base, extension = os.path.splitext(output_filename)
                
                counter = 1
                while os.path.exists(output_filename):
                    output_filename = f"{filename_base}-{counter}{extension}"
                    counter += 1
                
                self.output_filename = output_filename
                self.file_handle = open(self.output_filename, "wb+")
                vollog.info(f"Creating dump file: {self.output_filename}")
            
            def _get_final_filename(self):
                return self.output_filename
            
            def write(self, data):
                return self.file_handle.write(data)
            
            def read(self, size=-1):
                return self.file_handle.read(size)
                
            def seek(self, offset, whence=0):
                return self.file_handle.seek(offset, whence)
                
            def tell(self):
                return self.file_handle.tell()
                
            def close(self):
                if not self.file_handle.closed:
                    self.file_handle.close()
                super().close()
                
            def flush(self):
                return self.file_handle.flush()
                
            def seekable(self):
                return True
                
            def readable(self):
                return True
                
            def writable(self):
                return True

        
        # Save current directory
        original_dir = os.getcwd()
        
        try:
            
            # Reset context for clean run
            self.ctx = contexts.Context()
            
            # Re-initialize automagics with the new context
            self.automagics = automagic.available(self.ctx)
            
            # Set the single location (memory dump file)
            single_location = f"file://{os.path.abspath(file_path)}"
            self.ctx.config["automagic.LayerStacker.single_location"] = single_location
            
            # Use windows.pslist.PsList plugin for process dumping (procdump behavior)
            plugin_name = "windows.pslist.PsList"
            plugin_list = framework.list_plugins()
            plugin_class = plugin_list.get(plugin_name)
            
            if not plugin_class:
                raise ValueError(f"Plugin {plugin_name} not found")
            
            # Set up configuration for pslist
            base_config_path = "plugins"
            plugin_config_name = plugin_class.__name__
            
            # Filter by PID (pslist takes a list of PIDs)
            self.ctx.config[interfaces.configuration.path_join(base_config_path, plugin_config_name, "pid")] = [int(pid)]
            # Enable dump mode
            self.ctx.config[interfaces.configuration.path_join(base_config_path, plugin_config_name, "dump")] = True
            
            # Choose appropriate automagics
            automagics = automagic.choose_automagic(self.automagics, plugin_class)
            
            # Construct the plugin with FileHandler class
            plugin = framework_plugins.construct_plugin(
                self.ctx,
                automagics,
                plugin_class,
                base_config_path,
                progress_callback,  # Progress callback
                FileHandler  # Pass the class, not an instance
            )
            
            # Run the plugin - this will create dump files
            treegrid = plugin.run()
            
            # Iterate through results to trigger file creation
            # The FileHandler will be instantiated and used by the plugin during iteration
            file_count = 0
            if hasattr(treegrid, '_generator') and treegrid._generator is not None:
                for level, item in treegrid._generator:
                    file_count += 1
            
            vollog.info(f"Dumped process {pid} to {output_dir}")
            return output_dir
            
        finally:
            # Restore original directory
            os.chdir(original_dir)

    def dump_file(self, file_path: str, offset: str, output_dir: str, progress_callback=None) -> str:
        """
        Dump a specific file to disk using windows.dumpfiles plugin.
        
        Args:
            file_path: Path to the memory dump file
            offset: Virtual offset of the FILE_OBJECT
            output_dir: Directory to save the dumped file
            progress_callback: Optional callback function for progress reporting
            
        Returns:
            Path to the dumped directory
        """
        import os
        from volatility3.framework.interfaces import plugins as plugins_interface
        
        # Proper FileHandler implementation that inherits from FileHandlerInterface
        # and delegates to a real file object
        class FileHandler(plugins_interface.FileHandlerInterface):
            def __init__(self, filename: str):
                super().__init__(filename)
                self.output_dir = output_dir # output_dir is captured from the enclosing scope
                
                # Determine final filename immediately
                os.makedirs(self.output_dir, exist_ok=True)
                output_filename = os.path.join(self.output_dir, self.preferred_filename)
                filename_base, extension = os.path.splitext(output_filename)
                
                counter = 1
                while os.path.exists(output_filename):
                    output_filename = f"{filename_base}-{counter}{extension}"
                    counter += 1
                
                self.output_filename = output_filename
                self.file_handle = open(self.output_filename, "wb+")
                vollog.info(f"Creating dump file: {self.output_filename}")
            
            def _get_final_filename(self):
                return self.output_filename
            
            def write(self, data):
                return self.file_handle.write(data)
            
            def read(self, size=-1):
                return self.file_handle.read(size)
                
            def seek(self, offset, whence=0):
                return self.file_handle.seek(offset, whence)
                
            def tell(self):
                return self.file_handle.tell()
                
            def close(self):
                if not self.file_handle.closed:
                    self.file_handle.close()
                super().close()
                
            def flush(self):
                return self.file_handle.flush()
                
            def seekable(self):
                return True
                
            def readable(self):
                return True
                
            def writable(self):
                return True

        
        # Save current directory
        original_dir = os.getcwd()
        
        try:
            # Reset context for clean run
            self.ctx = contexts.Context()
            
            # Re-initialize automagics with the new context
            self.automagics = automagic.available(self.ctx)
            
            # Set the single location (memory dump file)
            single_location = f"file://{os.path.abspath(file_path)}"
            self.ctx.config["automagic.LayerStacker.single_location"] = single_location
            
            # Use windows.dumpfiles.DumpFiles plugin
            plugin_name = "windows.dumpfiles.DumpFiles"
            plugin_list = framework.list_plugins()
            plugin_class = plugin_list.get(plugin_name)
            
            if not plugin_class:
                raise ValueError(f"Plugin {plugin_name} not found")
            
            # Set up configuration for dumpfiles
            base_config_path = "plugins"
            plugin_config_name = plugin_class.__name__
            
            # Filter by virtual address (offset)
            # dumpfiles takes a list of integers for virtaddr
            try:
                # Handle hex string or int
                offset_val = int(offset, 16) if isinstance(offset, str) and offset.startswith('0x') else int(offset)
                self.ctx.config[interfaces.configuration.path_join(base_config_path, plugin_config_name, "virtaddr")] = [offset_val]
            except ValueError:
                raise ValueError(f"Invalid offset format: {offset}")
            
            # Choose appropriate automagics
            automagics = automagic.choose_automagic(self.automagics, plugin_class)
            
            # Construct the plugin with FileHandler class
            plugin = framework_plugins.construct_plugin(
                self.ctx,
                automagics,
                plugin_class,
                base_config_path,
                progress_callback,  # Progress callback
                FileHandler  # Pass the class, not an instance
            )
            
            # Run the plugin - this will create dump files
            treegrid = plugin.run()
            
            # Iterate through results to trigger file creation
            file_count = 0
            if hasattr(treegrid, '_generator') and treegrid._generator is not None:
                for level, item in treegrid._generator:
                    file_count += 1
            
            vollog.info(f"Dumped file at offset {offset} to {output_dir}")
            return output_dir
            
        finally:
            # Restore original directory
            os.chdir(original_dir)

    def get_available_plugins(self):
        return list(framework.list_plugins().keys())
