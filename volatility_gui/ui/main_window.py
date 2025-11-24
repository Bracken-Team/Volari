import os
import threading
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QLabel, QFileDialog, QToolBar, QStatusBar, QMessageBox, QProgressBar)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from volatility_gui.ui.process_tab import ProcessTab
from volatility_gui.ui.network_tab import NetworkTab
from volatility_gui.ui.osinfo_tab import OSInfoTab
from volatility_gui.ui.registry_tab import RegistryTab
from volatility_gui.ui.files_tab import FilesTab
from volatility_gui.ui.malware_tab import MalwareTab
from volatility_gui.logic.volatility_wrapper import VolatilityWrapper
from volatility_gui.logic.worker import PluginWorker
from volatility_gui.ui.log_viewer import LogViewer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Volatility 3 GUI")
        self.resize(1200, 800)
        
        # Initialize Wrapper
        self.vol_wrapper = VolatilityWrapper()
        self.current_dump_path = None
        self.worker = None
        
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

    def toggle_logs(self, checked):
        if checked:
            self.log_viewer.show()
        else:
            self.log_viewer.hide()

    def run_plugin(self, plugin_name, callback):
        if not self.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return

        self.statusBar().showMessage(f"Running {plugin_name}...")
        self.run_worker(self.vol_wrapper.run_plugin, callback, plugin_name)

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
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Ready")
        if callback:
            callback(result)
        self.worker = None

    def on_worker_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Error")
        QMessageBox.critical(self, "Error", error_msg)
        self.worker = None

    def update_progress(self, percentage, message):
        self.progress_bar.setValue(percentage)
        self.statusBar().showMessage(message)

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
    
    def open_settings(self):
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet.")
