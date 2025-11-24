import os
import threading
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QLabel, QFileDialog, QToolBar, QStatusBar, QMessageBox)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from volatility_gui.ui.process_tab import ProcessTab
from volatility_gui.ui.network_tab import NetworkTab
from volatility_gui.ui.osinfo_tab import OSInfoTab
from volatility_gui.ui.registry_tab import RegistryTab
from volatility_gui.ui.files_tab import FilesTab
from volatility_gui.ui.malware_tab import MalwareTab
from volatility_gui.logic.volatility_wrapper import VolatilityWrapper

class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Volatility 3 GUI")
        self.resize(1200, 800)
        
        # Initialize Wrapper
        self.vol_wrapper = VolatilityWrapper()
        self.current_dump_path = None
        
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

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Memory Dump", "", "All Files (*)")
        if file_name:
            self.current_dump_path = file_name
            self.statusBar().showMessage(f"Loaded: {file_name}")
            self.setWindowTitle(f"Volatility 3 GUI - {os.path.basename(file_name)}")

    def run_plugin(self, plugin_name, callback):
        if not self.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return

        self.statusBar().showMessage(f"Running {plugin_name}...")
        
        # TODO: Run in a separate thread to avoid freezing UI
        try:
            results = self.vol_wrapper.run_plugin(plugin_name, self.current_dump_path)
            callback(results)
            self.statusBar().showMessage(f"Finished {plugin_name}")
        except Exception as e:
            self.statusBar().showMessage(f"Error running {plugin_name}")
            QMessageBox.critical(self, "Error", str(e))

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
        
        try:
            output_file = self.vol_wrapper.dump_process(self.current_dump_path, pid, output_dir)
            self.statusBar().showMessage(f"Process dumped successfully")
            QMessageBox.information(self, "Success", f"Process {pid} dumped to:\n{output_file}")
        except Exception as e:
            self.statusBar().showMessage(f"Error dumping process")
            QMessageBox.critical(self, "Error", f"Failed to dump process {pid}:\n{str(e)}")
    
    def open_settings(self):
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet.")
