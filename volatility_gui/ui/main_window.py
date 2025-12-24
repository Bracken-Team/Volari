import os
import threading
import uuid
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QLabel, QFileDialog, QToolBar, QStatusBar, QMessageBox, QProgressBar, QDialog)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from volatility_gui.ui.process_tab import ProcessTab
from volatility_gui.ui.network_tab import NetworkTab
from volatility_gui.ui.osinfo_tab import OSInfoTab
from volatility_gui.ui.registry_tab import RegistryTab
from volatility_gui.ui.files_tab import FilesTab
from volatility_gui.ui.malware_tab import MalwareTab
from volatility_gui.ui.timeline_tab import TimelineTab
from volatility_gui.ui.ioc_tab import IOCTab
from volatility_gui.ui.virustotal_tab import VirusTotalTab
from volatility_gui.logic.volatility_wrapper import VolatilityWrapper
from volatility_gui.logic.worker import PluginWorker
from volatility_gui.ui.log_viewer import LogViewer
from volatility_gui.logic.investigation_queue import InvestigationQueue, InvestigationTask
from volatility_gui.ui.queue_viewer import QueueViewer
from volatility_gui.ui.report_config_dialog import ReportConfigDialog
from volatility_gui.logic.pdf_generator import PDFReportGenerator
from volatility_gui.logic.settings_manager import SettingsManager
from volatility_gui.ui.settings_dialog import SettingsDialog
from volatility_gui.logic.gc_worker import GarbageCollectionWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Volatility 3 GUI")
        self.resize(1200, 800)
        
        # Initialize Settings
        self.settings = SettingsManager()
        
        # Initialize Wrapper
        self.vol_wrapper = VolatilityWrapper()
        self.current_dump_path = None
        self.worker = None
        
        # Initialize Investigation Queue
        self.investigation_queue = InvestigationQueue()
        self.queue_viewer = None
        self.investigation_worker = None  # Store current investigation worker
        self.active_workers = []  # List of active workers for concurrent execution
        self.worker_map = {}  # Map task_id to worker for pause/stop operations
        # Load max concurrent tasks from settings
        self.MAX_CONCURRENT_TASKS = self.settings.get_max_concurrent_tasks()
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        layout = QVBoxLayout(central_widget)
        
        # Tab Widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Initialize Tabs
        self.init_tabs()
        
        # Toolbar
        self.init_toolbar()
        
        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
        
        # Log Viewer
        self.log_viewer = LogViewer(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_viewer)
        self.log_viewer.hide()
        
        # Queue Viewer
        self.queue_viewer = QueueViewer(self.investigation_queue, self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.queue_viewer)
        self.queue_viewer.hide()
        
        # Connect queue signals for global progress
        self.investigation_queue.task_started.connect(self.on_queue_task_started)
        self.investigation_queue.task_progress.connect(lambda tid, pct, msg: self.update_progress(pct, msg))
        self.investigation_queue.queue_completed.connect(self.on_queue_completed)

    def init_tabs(self):
        # OS Info Tab
        self.osinfo_tab = OSInfoTab()
        self.tabs.addTab(self.osinfo_tab, "OS Info")
        self.osinfo_tab.refresh_btn.clicked.connect(
            lambda: self.run_plugin("windows.info.Info", self.osinfo_tab.update_display)
        )
        
        # Processes Tab
        self.process_tab = ProcessTab()
        self.tabs.addTab(self.process_tab, "Processes")
        # Connect refresh button - use selected plugin
        self.process_tab.refresh_btn.clicked.connect(
            lambda: self.run_plugin(self.process_tab.get_selected_plugin(), self.process_tab.update_table)
        )
        # Connect dump button
        self.process_tab.dump_btn.clicked.connect(self.dump_process)
        
        # Network Tab
        self.network_tab = NetworkTab()
        self.tabs.addTab(self.network_tab, "Network")
        self.network_tab.refresh_btn.clicked.connect(
            lambda: self.run_plugin("windows.netscan.NetScan", self.network_tab.update_table)
        )
        
        # Registry Tab
        self.registry_tab = RegistryTab()
        self.tabs.addTab(self.registry_tab, "Registry")
        self.registry_tab.refresh_btn.clicked.connect(
            lambda: self.run_plugin(self.registry_tab.get_selected_plugin(), self.registry_tab.update_table)
        )
        
        # Files Tab
        self.files_tab = FilesTab()
        self.tabs.addTab(self.files_tab, "Files")
        self.files_tab.scan_btn.clicked.connect(
            lambda: self.run_plugin("windows.filescan.FileScan", self.files_tab.update_table)
        )
        
        # Malware Tab
        self.malware_tab = MalwareTab()
        self.tabs.addTab(self.malware_tab, "Malware")
        self.malware_tab.scan_btn.clicked.connect(
            lambda: self.run_plugin(self.malware_tab.get_selected_plugin(), self.malware_tab.update_table)
        )
        
        # Timeline Tab
        self.timeline_tab = TimelineTab()
        self.tabs.addTab(self.timeline_tab, "Timeline")
        self.timeline_tab.generate_btn.clicked.connect(self.generate_timeline_from_data)

        # IOC Tab
        self.ioc_tab = IOCTab()
        self.tabs.addTab(self.ioc_tab, "IOC Checker")
        self.ioc_tab.scan_btn.clicked.connect(self.run_ioc_scan)
        
        # VirusTotal Tab
        self.virustotal_tab = VirusTotalTab()
        self.tabs.addTab(self.virustotal_tab, "VirusTotal")

    def init_process_tab(self):
        layout = QVBoxLayout(self.process_tab)
        label = QLabel("Processes will be listed here")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

    def init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Load Image Action
        load_action = QAction("Load Memory Dump", self)
        load_action.setStatusTip("Open a memory dump file")
        load_action.triggered.connect(self.load_image)
        toolbar.addAction(load_action)
        
        # Settings Action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
        
        # Show Logs Action
        logs_action = QAction("Show Logs", self)
        logs_action.setCheckable(True)
        logs_action.triggered.connect(self.toggle_logs)
        toolbar.addAction(logs_action)
        
        # Show Queue Action
        queue_action = QAction("Show Queue", self)
        queue_action.setCheckable(True)
        queue_action.triggered.connect(self.toggle_queue)
        toolbar.addAction(queue_action)
        
        toolbar.addSeparator()
        
        # Auto Investigate Action
        auto_investigate_action = QAction("Auto Investigate", self)
        auto_investigate_action.setStatusTip("Run essential plugins automatically")
        auto_investigate_action.triggered.connect(self.auto_investigate)
        toolbar.addAction(auto_investigate_action)
        
        toolbar.addSeparator()
        
        # Generate Report Action
        report_action = QAction("Generate Report", self)
        report_action.setStatusTip("Generate PDF forensic report")
        report_action.triggered.connect(self.generate_report)
        toolbar.addAction(report_action)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Memory Dump", "", "All Files (*)")
        if file_name:
            self.current_dump_path = file_name
            self.statusBar().showMessage(f"Loading: {file_name}...")
            
            # Load file in background to avoid freezing
            # Since loading might take time (automagics), we can use the worker too
            # But for now, let's just call it directly as it's usually fast enough for initial load
            # Or better, wrap it in a worker if it's slow. Automagics can be slow.
            # Let's run it in a thread.
            
            self.run_worker(self.vol_wrapper.load_file, self.on_load_finished, file_name)

    def on_load_finished(self, result):
        self.statusBar().showMessage(f"Loaded: {self.current_dump_path}")
        self.setWindowTitle(f"Volatility 3 GUI - {os.path.basename(self.current_dump_path)}")
        QMessageBox.information(self, "File Loaded", f"Successfully loaded memory dump:\n{os.path.basename(self.current_dump_path)}")

    def toggle_logs(self, checked):
        if checked:
            self.log_viewer.show()
        else:
            self.log_viewer.hide()
            
    def toggle_queue(self, checked):
        if checked:
            self.queue_viewer.show()
        else:
            self.queue_viewer.hide()

    def run_plugin(self, plugin_name, callback):
        if not self.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return

        # Create task for the plugin
        task_id = str(uuid.uuid4())
        task_name = plugin_name.split('.')[-1]  # Use last part of plugin name as task name
        
        task = InvestigationTask(
            task_id,
            task_name,
            plugin_name,
            self.vol_wrapper.run_plugin,
            plugin_name
        )
        task.callback = callback
        
        # Add to queue
        self.investigation_queue.add_task(task)
        self.statusBar().showMessage(f"Added {task_name} to queue")
        
        # Ensure queue viewer is updated (it listens to signals)
        self.queue_viewer.show()
        
        # Start processing if not already running
        if not self.investigation_worker:
            self.process_next_task()

    def run_worker(self, func, callback, *args, **kwargs):
        """Run a function in a background thread."""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Busy", "A task is already running. Please wait.")
            return

        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        self.worker = PluginWorker(func, *args, **kwargs)
        self.worker.started.connect(lambda: self.statusBar().showMessage("Processing..."))
        self.worker.finished.connect(lambda result: self.on_worker_finished(result, callback))
        self.worker.error.connect(self.on_worker_error)
        self.worker.progress.connect(self.update_progress)
        self.worker.start()

    def on_worker_finished(self, result, callback):
        # Only hide if queue is not running
        if not self.investigation_queue.active_task_ids:
            self.progress_bar.setVisible(False)
            self.statusBar().showMessage("Ready")
            
        if callback:
            callback(result)
        self.worker = None

    def on_worker_error(self, error_msg):
        # Only hide if queue is not running
        if not self.investigation_queue.active_task_ids:
            self.progress_bar.setVisible(False)
            self.statusBar().showMessage("Error")
            
        QMessageBox.critical(self, "Error", error_msg)
        self.worker = None

    def update_progress(self, percentage, message):
        if percentage == -1:
            self.progress_bar.setRange(0, 0)  # Indeterminate mode
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(percentage)
        self.statusBar().showMessage(message)

    def on_queue_task_started(self, task_id):
        """Handle queue task started."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.statusBar().showMessage("Processing queue...")
        
    def on_queue_completed(self):
        """Handle queue completion."""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Queue processing complete")

    def dump_process(self):
        """Dump the selected process to a file."""
        if not self.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return
        
        pid = self.process_tab.get_selected_pid()
        if not pid:
            QMessageBox.warning(self, "Error", "Please select a process to dump.")
            return
        
        # Ask user for output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return
        
        self.statusBar().showMessage(f"Dumping process {pid}...")
        
        # Run in worker
        self.run_worker(
            self.vol_wrapper.dump_process, 
            lambda res: QMessageBox.information(self, "Success", f"Process {pid} dumped to:\n{res}"),
            self.current_dump_path, pid, output_dir
        )
    
    def auto_investigate(self):
        """Run essential plugins automatically for quick triage."""
        if not self.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return
            
        # Get plugin list from settings
        plugin_list = self.settings.get_auto_investigation_plugins()
        
        # Build plugin display names for confirmation dialog
        plugin_names = []
        for plugin in plugin_list:
            name = plugin.split('.')[-1]  # Get last part (e.g., "PsList" from "windows.pslist.PsList")
            plugin_names.append(f"• {name}")
        
        # Ask user for confirmation
        reply = QMessageBox.question(
            self, 
            "Auto Investigation",
            f"Auto Investigation will run the following plugins:\n\n" +
            "\n".join(plugin_names) + "\n\n" +
            "This may take several minutes. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        # Clear previous queue
        self.investigation_queue.clear_queue()
        
        # Create tasks for essential plugins
        import uuid
        import gc
        
        # Map plugins to their callbacks
        plugin_callbacks = {
            "windows.info.Info": self.osinfo_tab.update_display,
            "windows.pslist.PsList": lambda data: self.process_tab.update_table(data, plugin_name="PS List"),
            "windows.netscan.NetScan": self.network_tab.update_table,
            "windows.filescan.FileScan": self.files_tab.update_table,
            "windows.handles.Handles": lambda data: self.process_tab.update_table(data, plugin_name="Handles"),
            "windows.registry.hivelist.HiveList": lambda data: self.registry_tab.update_table(data, plugin_name="Hive List"),
        }
        
        tasks = []
        for plugin_name in plugin_list:
            task_name = plugin_name.split('.')[-1]  # Extract simple name
            callback = plugin_callbacks.get(plugin_name, lambda data: None)  # Default to no-op
            tasks.append((task_name, plugin_name, callback))
        
        for task_name, plugin_name, callback in tasks:
            task_id = str(uuid.uuid4())
            task = InvestigationTask(
                task_id,
                task_name,
                plugin_name,
                self.vol_wrapper.run_plugin,
                plugin_name  # positional arg for run_plugin function
            )
            task.callback = callback  # Store callback for later use
            self.investigation_queue.add_task(task)
            
        # Show queue viewer
        self.queue_viewer.show()
        
        # Start processing queue
        self.process_next_task()
        
    def run_gc_and_continue(self):
        """Run garbage collection in background then continue processing."""
        self.gc_worker = GarbageCollectionWorker()
        self.gc_worker.finished.connect(self.process_next_task)
        # Using a lambda to cleanup the worker ref
        self.gc_worker.finished.connect(lambda: setattr(self, 'gc_worker', None))
        self.gc_worker.start()

    def process_next_task(self):
        """Process the next task in the investigation queue."""
        # Check if we can start more tasks
        if len(self.active_workers) >= self.MAX_CONCURRENT_TASKS:
            return

        pending_tasks = self.investigation_queue.get_pending_tasks()
        
        if not pending_tasks and not self.active_workers:
            # All tasks done and no workers running
            summary = self.investigation_queue.get_summary()
            msg = f"Investigation queue finished. Completed: {summary['completed']}, Failed: {summary['failed']}"
            self.statusBar().showMessage(msg)
            
            # Only show popup if it was a significant batch (more than 1 task total)
            # or if we explicitly want to notify (like auto investigation)
            if summary['total'] > 1:
                QMessageBox.information(
                    self,
                    "Investigation Complete",
                    "Queue processing completed!\n\n"
                    f"Total tasks: {summary['total']}\n"
                    f"Completed: {summary['completed']}\n"
                    f"Failed: {summary['failed']}"
                )
            return
            
        # Start tasks until we reach max concurrency or run out of pending tasks
        while pending_tasks and len(self.active_workers) < self.MAX_CONCURRENT_TASKS:
            # Get next task
            task = pending_tasks.pop(0)
            self.investigation_queue.mark_started(task.task_id)
            
            # Create worker for this task
            worker = PluginWorker(task.func, *task.args, **task.kwargs)
            self.active_workers.append(worker)
            self.worker_map[task.task_id] = worker
            
            # Define callbacks with closure to capture specific task and worker
            def on_task_complete(result, t=task, w=worker):
                # Update callback with result
                if hasattr(t, 'callback') and t.callback:
                    t.callback(result)
                self.investigation_queue.mark_completed(t.task_id, result)
                
                # Clean up worker
                if w in self.active_workers:
                    self.active_workers.remove(w)
                if t.task_id in self.worker_map:
                    del self.worker_map[t.task_id]
                
                # Process next task (with intermediate GC for stability)
                # Running GC in background prevents memory exhaustion while keeping UI responsive
                self.run_gc_and_continue()
                
            def on_task_error(error, t=task, w=worker):
                self.investigation_queue.mark_failed(t.task_id, str(error))
                
                # Clean up worker
                if w in self.active_workers:
                    self.active_workers.remove(w)
                if t.task_id in self.worker_map:
                    del self.worker_map[t.task_id]
                
                # Continue with next task even if this one failed
                self.process_next_task()

            worker.finished.connect(on_task_complete)
            worker.error.connect(on_task_error)
            worker.progress.connect(lambda pct, msg, tid=task.task_id: self.investigation_queue.update_progress(tid, pct, msg))
            worker.start()
    
    def pause_worker(self, task_id: str):
        """Pause/stop a worker for a specific task."""
        if task_id in self.worker_map:
            worker = self.worker_map[task_id]
            
            # Note: We can't truly pause a running thread in Python
            # Instead, we disconnect signals and clean up
            # The task will be marked as paused and can be resumed later
            
            try:
                worker.finished.disconnect()
                worker.error.disconnect()
                worker.progress.disconnect()
            except:
                pass  # Signals might already be disconnected
            
            # Clean up
            if worker in self.active_workers:
                self.active_workers.remove(worker)
            del self.worker_map[task_id]
            
            # The worker will continue running but we won't process its results
            # When resumed, a new worker will be created
    
    def generate_report(self):
        """Generate a PDF forensic report."""
        if not self.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return
            
        # Show configuration dialog
        dialog = ReportConfigDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        config = dialog.get_config()
        
        # Collect data from tabs based on configuration
        system_info = None
        processes = None
        network = None
        registry = None
        files = None
        
        if config['include_system_info']:
            # Get system info from OS Info tab
            if hasattr(self.osinfo_tab, 'system_info'):
                system_info = self.osinfo_tab.system_info
                
        if config['include_processes']:
            # Get process data from Process tab
            if hasattr(self.process_tab, 'plugin_data_cache'):
                # Get data from PS List (or first available)
                for plugin_name in ['PS List', 'PS Scan', 'PS Tree']:
                    if self.process_tab.plugin_data_cache.get(plugin_name):
                        processes = self.process_tab.plugin_data_cache[plugin_name]
                        break
                        
        if config['include_network']:
            # Get network data
            if hasattr(self.network_tab, 'current_data'):
                network = self.network_tab.current_data
                
        if config['include_registry']:
            # Get registry data
            if hasattr(self.registry_tab, 'plugin_data_cache'):
                for plugin_name in ['Hive List', 'Hive Scan']:
                    if self.registry_tab.plugin_data_cache.get(plugin_name):
                        registry = self.registry_tab.plugin_data_cache[plugin_name]
                        break
                        
        if config['include_files']:
            # Get file data
            if hasattr(self.files_tab, 'current_data'):
                files = self.files_tab.current_data
        
        # Check if we have any data
        if not any([system_info, processes, network, registry, files]):
            reply = QMessageBox.question(
                self,
                "No Data Available",
                "No analysis data is currently available. Would you like to run Auto Investigation first?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.auto_investigate()
            return
        
        # Generate the report
        self.statusBar().showMessage("Generating PDF report...")
        
        try:
            success = PDFReportGenerator.create_forensic_report(
                output_path=config['output_path'],
                dump_file=self.current_dump_path,
                system_info=system_info,
                processes=processes,
                network=network,
                registry=registry,
                files=files,
                case_name=config['case_name'],
                analyst=config['analyst'],
                notes=config['notes']
            )
            
            if success:
                self.statusBar().showMessage("Report generated successfully!")
                QMessageBox.information(
                    self,
                    "Report Generated",
                    f"PDF report has been saved to:\n{config['output_path']}"
                )
            else:
                self.statusBar().showMessage("Report generation failed")
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to generate PDF report. Please check the logs for details."
                )
        except Exception as e:
            self.statusBar().showMessage("Report generation failed")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate PDF report:\n{str(e)}"
            )
    
    def generate_timeline_from_data(self):
        """Generate timeline from cached analysis data."""
        if not self.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return
            
        # Collect data from tabs
        process_data = None
        network_data = None
        file_data = None
        registry_data = None
        
        # Get process data
        if hasattr(self.process_tab, 'plugin_data_cache'):
            for plugin_name in ['PS List', 'PS Scan', 'PS Tree']:
                if self.process_tab.plugin_data_cache.get(plugin_name):
                    process_data = self.process_tab.plugin_data_cache[plugin_name]
                    break
                    
        # Get network data
        if hasattr(self.network_tab, 'current_data'):
            network_data = self.network_tab.current_data
            
        # Get file data
        if hasattr(self.files_tab, 'current_data'):
            file_data = self.files_tab.current_data
            
        # Get registry data
        if hasattr(self.registry_tab, 'plugin_data_cache'):
            for plugin_name in ['Hive List', 'Hive Scan']:
                if self.registry_tab.plugin_data_cache.get(plugin_name):
                    registry_data = self.registry_tab.plugin_data_cache[plugin_name]
                    break
        
        # Check if we have any data
        if not any([process_data, network_data, file_data, registry_data]):
            reply = QMessageBox.question(
                self,
                "No Data Available",
                "No analysis data is currently available. Would you like to run Auto Investigation first?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.auto_investigate()
            return
            
        # Generate timeline
        self.timeline_tab.load_data(
            process_data=process_data,
            network_data=network_data,
            file_data=file_data,
            registry_data=registry_data
        )
        
        # Switch to timeline tab
        self.tabs.setCurrentWidget(self.timeline_tab)
    
    def open_settings(self):
        """Open comprehensive settings dialog."""
        # Get VT scanner if available
        vt_scanner = None
        if hasattr(self, 'virustotal_tab') and hasattr(self.virustotal_tab, 'scanner'):
            vt_scanner = self.virustotal_tab.scanner
            
        dialog = SettingsDialog(self.settings, vt_scanner, self)
        if dialog.exec():
            # Settings were saved, apply them
            self.apply_settings()
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.\n\nSome changes may require a restart to take effect.")
            
    def apply_settings(self):
        """Apply settings to various components."""
        # Update max concurrent tasks
        self.MAX_CONCURRENT_TASKS = self.settings.get_max_concurrent_tasks()
        
        # Update VirusTotal scanner API key
        if hasattr(self, 'virustotal_tab') and hasattr(self.virustotal_tab, 'scanner'):
            api_key = self.settings.get_vt_api_key()
            if api_key:
                self.virustotal_tab.scanner.set_api_key(api_key)

    def run_ioc_scan(self):
        """Run IOC scan against all loaded data."""
        if not self.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return
            
        # Collect data from all tabs
        all_matches = []
        scanner = self.ioc_tab.scanner
        
        # Scan Process Data
        # We need to check all cached process data
        for plugin, data in self.process_tab.plugin_data_cache.items():
            if data:
                matches = scanner.scan_data(data, f"Process: {plugin}")
                all_matches.extend(matches)
                
        # Scan Network Data
        if hasattr(self.network_tab, 'current_data') and self.network_tab.current_data:
            matches = scanner.scan_data(self.network_tab.current_data, "Network Scan")
            all_matches.extend(matches)
            
        # Scan File Data
        if hasattr(self.files_tab, 'current_data') and self.files_tab.current_data:
            matches = scanner.scan_data(self.files_tab.current_data, "File Scan")
            all_matches.extend(matches)
            
        # Scan Registry Data
        for plugin, data in self.registry_tab.plugin_data_cache.items():
            if data:
                matches = scanner.scan_data(data, f"Registry: {plugin}")
                all_matches.extend(matches)
                
        # Display results
        self.ioc_tab.display_results(all_matches)
        
        if not all_matches:
            QMessageBox.information(self, "Scan Complete", "No IOC matches found in the currently loaded data.")
        else:
            QMessageBox.information(self, "Scan Complete", f"Found {len(all_matches)} IOC matches!")
