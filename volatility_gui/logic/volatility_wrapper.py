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
            return self._process_treegrid(treegrid, progress_callback)
            
        except Exception as e:
            vollog.error(f"Error running plugin {plugin_name}: {e}")
            raise e

    def _process_treegrid(self, treegrid: interfaces.renderers.TreeGrid, progress_callback=None, max_rows=50000) -> List[Dict[str, Any]]:
        """
        Converts a TreeGrid to a list of dictionaries.
        
        Args:
            treegrid: The TreeGrid to process
            progress_callback: Optional callback for progress updates
            max_rows: Maximum number of rows to process (default 50000 to prevent extreme memory issues)
        """
        results = []
        
        # Get column names
        columns = [col.name for col in treegrid.columns]
        
        # Access the internal generator that was passed to the TreeGrid
        # The generator yields (level, values) tuples
        try:
            if hasattr(treegrid, '_generator') and treegrid._generator is not None:
                count = 0
                for level, item in treegrid._generator:
                    # Stop if we've reached the maximum
                    if count >= max_rows:
                        vollog.warning(f"Reached maximum row limit ({max_rows}). Truncating results.")
                        if progress_callback:
                            progress_callback(-1, f"Truncated at {max_rows} rows")
                        break
                        
                    row = {}
                    for i, value in enumerate(item):
                        try:
                            row[columns[i]] = str(value)
                        except Exception as e:
                            vollog.warning(f"Error converting value at index {i}: {e}")
                            row[columns[i]] = "N/A"
                    results.append(row)
                    
                    count += 1
                    if progress_callback and count % 10 == 0:
                        progress_callback(-1, f"Processing results: {count} rows")
                        
            else:
                vollog.error("TreeGrid has no _generator attribute or it's None")
        except Exception as e:
            vollog.error(f"Error iterating TreeGrid: {e}")
            import traceback
            vollog.error(traceback.format_exc())
        
        vollog.info(f"Processed {len(results)} rows from TreeGrid")
        return results

    def dump_process(self, file_path: str, pid: str, output_dir: str, progress_callback=None) -> str:
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
    def calculate_file_hash(self, file_path: str, offset: str) -> str:
        """
        Calculate SHA256 hash of a file from memory dump.
        
        Args:
            file_path: Path to the memory dump file
            offset: Virtual offset of the FILE_OBJECT
            
        Returns:
            SHA256 hash string or None if failed
        """
        import tempfile
        import shutil
        import hashlib
        
        temp_dir = tempfile.mkdtemp()
        try:
            # Dump file to temp dir
            dumped_dir = self.dump_file(file_path, offset, temp_dir)
            
            # Find the dumped file (should be the only one or first one)
            files = [f for f in os.listdir(dumped_dir) if os.path.isfile(os.path.join(dumped_dir, f))]
            if not files:
                return None
                
            dumped_file_path = os.path.join(dumped_dir, files[0])
            
            # Calculate hash
            sha256_hash = hashlib.sha256()
            with open(dumped_file_path, "rb") as f:
                # Read in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
                    
            return sha256_hash.hexdigest()
            
        except Exception as e:
            vollog.error(f"Error calculating file hash: {e}")
            return None
        finally:
            # Cleanup
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                vollog.error(f"Error cleaning up temp dir: {e}")
    def calculate_process_hash(self, file_path: str, pid: str) -> str:
        """
        Calculate SHA256 hash of a process executable from memory dump.
        
        Args:
            file_path: Path to the memory dump file
            pid: Process ID
            
        Returns:
            SHA256 hash string or None if failed
        """
        import tempfile
        import shutil
        import hashlib
        
        temp_dir = tempfile.mkdtemp()
        try:
            # Dump process to temp dir
            dumped_dir = self.dump_process(file_path, pid, temp_dir)
            
            # Find the dumped file (should be the executable)
            files = [f for f in os.listdir(dumped_dir) if os.path.isfile(os.path.join(dumped_dir, f))]
            if not files:
                return None
            
            # If multiple files, try to find the .exe or .img
            target_file = files[0]
            for f in files:
                if f.endswith('.exe') or f.endswith('.img'):
                    target_file = f
                    break
                    
            dumped_file_path = os.path.join(dumped_dir, target_file)
            
            # Calculate hash
            sha256_hash = hashlib.sha256()
            with open(dumped_file_path, "rb") as f:
                # Read in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
                    
            return sha256_hash.hexdigest()
            
        except Exception as e:
            vollog.error(f"Error calculating process hash: {e}")
            return None
        finally:
            # Cleanup
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                vollog.error(f"Error cleaning up temp dir: {e}")
