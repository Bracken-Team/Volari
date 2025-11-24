import os
import threading
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QLabel, QFileDialog, QToolBar, QStatusBar, QMessageBox)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from volatility_gui.ui.process_tab import ProcessTab
from volatility_gui.ui.network_tab import NetworkTab
from volatility_gui.ui.virustotal_tab import VirusTotalTab
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
        # Processes Tab
        self.process_tab = ProcessTab()
        self.tabs.addTab(self.process_tab, "Processes")
        self.process_tab.refresh_btn.clicked.connect(lambda: self.run_plugin("windows.pslist.PsList", self.process_tab.update_table))
        
        # Network Tab
        self.network_tab = NetworkTab()
        self.tabs.addTab(self.network_tab, "Network")
        
        # VirusTotal Tab
        self.vt_tab = QWidget()
        self.tabs.addTab(self.vt_tab, "VirusTotal")
        
        # Reports Tab
        self.reports_tab = QWidget()
        self.tabs.addTab(self.reports_tab, "Reports")

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
            self.statusBar().showMessage(f"Loaded: {file_name}")
            # TODO: Trigger analysis

    def open_settings(self):
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet.")
