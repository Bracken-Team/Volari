from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                             QProgressBar, QLineEdit, QMessageBox, QGroupBox, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QDesktopServices, QAction
from PyQt6.QtCore import QUrl
from volatility_gui.logic.virustotal_scanner import VirusTotalScanner
from volatility_gui.ui.vt_settings_dialog import VTSettingsDialog
from volatility_gui.logic.exporter import Exporter
from typing import List, Dict, Any


class ScanWorker(QThread):
    """Worker thread for scanning hashes."""
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(list)  # results
    error = pyqtSignal(str)
    
    def __init__(self, scanner: VirusTotalScanner, hashes: List[str]):
        super().__init__()
        self.scanner = scanner
        self.hashes = hashes
        
    def run(self):
        """Run the scan."""
        try:
            results = self.scanner.scan_hashes_batch(
                self.hashes,
                progress_callback=lambda c, t, m: self.progress.emit(c, t, m)
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class VirusTotalTab(QWidget):
    """Tab for VirusTotal hash scanning."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scanner = VirusTotalScanner()
        self.scan_worker = None
        self.results = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # API Key Status Section
        status_group = QGroupBox("VirusTotal Status")
        status_layout = QHBoxLayout()
        
        self.api_status_label = QLabel("⚠️ API Key Not Configured")
        self.api_status_label.setStyleSheet("font-weight: bold; color: #FF9800;")
        status_layout.addWidget(self.api_status_label)
        
        status_layout.addStretch()
        
        config_btn = QPushButton("⚙️ Configure API Key")
        config_btn.clicked.connect(self.open_settings)
        status_layout.addWidget(config_btn)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Scan Controls
        controls_group = QGroupBox("Scan Controls")
        controls_layout = QVBoxLayout()
        
        # Load hashes buttons
        load_layout = QHBoxLayout()
        load_layout.addWidget(QLabel("Load Hashes:"))
        
        load_files_btn = QPushButton("📁 From Files Tab")
        load_files_btn.clicked.connect(self.load_from_files)
        load_layout.addWidget(load_files_btn)
        
        load_process_btn = QPushButton("⚙️ From Process Tab")
        load_process_btn.clicked.connect(self.load_from_process)
        load_layout.addWidget(load_process_btn)
        
        load_layout.addStretch()
        controls_layout.addLayout(load_layout)
        
        # Manual hash input
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("Or enter hash manually:"))
        
        self.manual_hash_input = QLineEdit()
        self.manual_hash_input.setPlaceholderText("Enter MD5, SHA1, or SHA256 hash...")
        manual_layout.addWidget(self.manual_hash_input)
        
        add_hash_btn = QPushButton("➕ Add Hash")
        add_hash_btn.clicked.connect(self.add_manual_hash)
        manual_layout.addWidget(add_hash_btn)
        
        controls_layout.addLayout(manual_layout)
        
        # Scan button and progress
        scan_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("🔍 Scan All Hashes")
        self.scan_btn.clicked.connect(self.start_scan)
        self.scan_btn.setEnabled(False)
        scan_layout.addWidget(self.scan_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        scan_layout.addWidget(self.progress_bar)
        
        controls_layout.addLayout(scan_layout)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by hash, filename, or status...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Hash", "Source", "Detections", "Engines", "Status", "VT Link"
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.clicked.connect(lambda: self.export_results("csv"))
        export_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("Export JSON")
        export_json_btn.clicked.connect(lambda: self.export_results("json"))
        export_layout.addWidget(export_json_btn)
        
        layout.addLayout(export_layout)
        
        # Update API status
        self.update_api_status()
        
    def update_api_status(self):
        """Update the API key status indicator."""
        if self.scanner.api_key:
            self.api_status_label.setText("✅ API Key Configured")
            self.api_status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        else:
            self.api_status_label.setText("⚠️ API Key Not Configured")
            self.api_status_label.setStyleSheet("font-weight: bold; color: #FF9800;")
            
    def open_settings(self):
        """Open the settings dialog."""
        dialog = VTSettingsDialog(self.scanner, self)
        if dialog.exec():
            self.update_api_status()
            
    def load_from_files(self):
        """Load hashes from the Files tab."""
        # Get parent main window
        main_window = self.window()
        if not hasattr(main_window, 'files_tab'):
            QMessageBox.warning(self, "Error", "Files tab not found")
            return
            
        # Get file data
        files_data = main_window.files_tab.current_data
        if not files_data:
            QMessageBox.information(self, "No Data", "No file data available. Please run filescan first.")
            return
            
        # Extract hashes (look for common hash column names)
        hashes = []
        for item in files_data:
            # Try different possible hash field names
            hash_value = item.get('MD5') or item.get('SHA256') or item.get('Hash') or item.get('hash')
            if hash_value:
                hashes.append(hash_value)
                
        if not hashes:
            QMessageBox.warning(self, "No Hashes", "No hashes found in file data.")
            return
            
        self.add_hashes_to_table(hashes, "Files")
        QMessageBox.information(self, "Success", f"Loaded {len(hashes)} hashes from Files tab")
        
    def load_from_process(self):
        """Load hashes from the Process tab."""
        # Get parent main window
        main_window = self.window()
        if not hasattr(main_window, 'process_tab'):
            QMessageBox.warning(self, "Error", "Process tab not found")
            return
            
        # Get process data
        process_data = None
        if hasattr(main_window.process_tab, 'plugin_data_cache'):
            for plugin_name in ['PS List', 'PS Scan']:
                if main_window.process_tab.plugin_data_cache.get(plugin_name):
                    process_data = main_window.process_tab.plugin_data_cache[plugin_name]
                    break
                    
        if not process_data:
            QMessageBox.information(self, "No Data", "No process data available. Please run pslist first.")
            return
            
        # Extract hashes
        hashes = []
        for item in process_data:
            hash_value = item.get('MD5') or item.get('SHA256') or item.get('Hash') or item.get('hash')
            if hash_value:
                hashes.append(hash_value)
                
        if not hashes:
            QMessageBox.warning(self, "No Hashes", "No hashes found in process data.")
            return
            
        self.add_hashes_to_table(hashes, "Processes")
        QMessageBox.information(self, "Success", f"Loaded {len(hashes)} hashes from Process tab")
        
    def add_hashes_to_table(self, hashes: List[str], source: str):
        """Add hashes to the table for scanning."""
        for hash_value in hashes:
            # Check if already in table
            found = False
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).text() == hash_value:
                    found = True
                    break
                    
            if not found:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(hash_value))
                self.table.setItem(row, 1, QTableWidgetItem(source))
                self.table.setItem(row, 2, QTableWidgetItem("-"))
                self.table.setItem(row, 3, QTableWidgetItem("-"))
                self.table.setItem(row, 4, QTableWidgetItem("Pending"))
                self.table.setItem(row, 5, QTableWidgetItem(""))
                
        self.scan_btn.setEnabled(self.table.rowCount() > 0 and self.scanner.api_key is not None)
        
    def add_manual_hash(self):
        """Add a manually entered hash to the table."""
        hash_value = self.manual_hash_input.text().strip()
        
        if not hash_value:
            QMessageBox.warning(self, "No Hash", "Please enter a hash value.")
            return
            
        # Basic validation - check if it looks like a hash
        if len(hash_value) not in [32, 40, 64]:  # MD5=32, SHA1=40, SHA256=64
            QMessageBox.warning(
                self,
                "Invalid Hash",
                "Hash must be 32 (MD5), 40 (SHA1), or 64 (SHA256) characters long."
            )
            return
            
        # Add to table
        self.add_hashes_to_table([hash_value], "Manual Entry")
        self.manual_hash_input.clear()
        
    def start_scan(self):
        """Start scanning all hashes."""
        if not self.scanner.api_key:
            QMessageBox.warning(self, "No API Key", "Please configure your API key first.")
            self.open_settings()
            return
            
        # Get all hashes
        hashes = []
        for row in range(self.table.rowCount()):
            hash_value = self.table.item(row, 0).text()
            hashes.append(hash_value)
            
        if not hashes:
            return
            
        # Start scan
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(hashes))
        self.progress_bar.setValue(0)
        
        self.scan_worker = ScanWorker(self.scanner, hashes)
        self.scan_worker.progress.connect(self.update_progress)
        self.scan_worker.finished.connect(self.scan_finished)
        self.scan_worker.error.connect(self.scan_error)
        self.scan_worker.start()
        
    def update_progress(self, current: int, total: int, message: str):
        """Update scan progress."""
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"{current}/{total} - {message}")
        
    def scan_finished(self, results: List[Dict[str, Any]]):
        """Handle scan completion."""
        self.results = results
        
        # Update table with results
        for result in results:
            hash_value = result.get("hash")
            
            # Find row
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).text() == hash_value:
                    # Update cells
                    detections = result.get("detections", 0)
                    total_engines = result.get("total_engines", 0)
                    
                    self.table.setItem(row, 2, QTableWidgetItem(str(detections)))
                    self.table.setItem(row, 3, QTableWidgetItem(str(total_engines)))
                    
                    # Status
                    if result.get("error"):
                        status = "Error"
                        color = QColor(255, 200, 200)
                    elif result.get("not_found"):
                        status = "Not Found"
                        color = QColor(220, 220, 220)
                    elif detections == 0:
                        status = "Clean"
                        color = QColor(200, 255, 200)
                    elif detections <= 5:
                        status = "Suspicious"
                        color = QColor(255, 255, 200)
                    else:
                        status = "Malicious"
                        color = QColor(255, 200, 200)
                        
                    status_item = QTableWidgetItem(status)
                    if result.get("error"):
                        status_item.setToolTip(result.get("error"))
                    status_item.setBackground(color)
                    self.table.setItem(row, 4, status_item)
                    
                    # VT Link
                    link_item = QTableWidgetItem("View Report")
                    self.table.setItem(row, 5, link_item)
                    break
                    
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        # Show summary
        malicious = sum(1 for r in results if r.get("malicious", 0) > 5)
        suspicious = sum(1 for r in results if 0 < r.get("detections", 0) <= 5)
        clean = sum(1 for r in results if r.get("detections", 0) == 0)
        
        QMessageBox.information(
            self,
            "Scan Complete",
            f"Scan completed!\n\n"
            f"Malicious: {malicious}\n"
            f"Suspicious: {suspicious}\n"
            f"Clean: {clean}"
        )
        
    def scan_error(self, error: str):
        """Handle scan error."""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        QMessageBox.critical(self, "Scan Error", f"An error occurred during scanning:\n\n{error}")
        
    def filter_table(self):
        """Filter table based on search input."""
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            show = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    show = True
                    break
            self.table.setRowHidden(row, not show)
            
    def show_context_menu(self, position):
        """Show context menu for table."""
        menu = QMenu()
        
        open_vt_action = QAction("🌐 Open in VirusTotal", self)
        open_vt_action.triggered.connect(self.open_in_virustotal)
        menu.addAction(open_vt_action)
        
        copy_hash_action = QAction("📋 Copy Hash", self)
        copy_hash_action.triggered.connect(self.copy_hash)
        menu.addAction(copy_hash_action)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
        
    def open_in_virustotal(self):
        """Open selected hash in VirusTotal."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            hash_value = self.table.item(row, 0).text()
            url = f"https://www.virustotal.com/gui/file/{hash_value}"
            QDesktopServices.openUrl(QUrl(url))
            
    def copy_hash(self):
        """Copy selected hash to clipboard."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            hash_value = self.table.item(row, 0).text()
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(hash_value)
            
    def export_results(self, format_type: str):
        """Export results to file."""
        if not self.results:
            QMessageBox.warning(self, "No Results", "No scan results to export.")
            return
            
        exporter = Exporter()
        if format_type == "csv":
            success = exporter.export_csv(self.results, "virustotal_results.csv")
        elif format_type == "json":
            success = exporter.export_json(self.results, "virustotal_results.json")
        else:
            return
            
        if success:
            QMessageBox.information(self, "Success", f"Results exported to {format_type.upper()}")
