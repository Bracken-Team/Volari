from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel, QFileDialog, QMessageBox, QLineEdit,
                             QMenu)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
import os
from volatility_gui.logic.exporter import Exporter

class FilesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_data = None  # Cache for export
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Controls area
        controls_layout = QHBoxLayout()
        self.status_label = QLabel("Ready to analyze")
        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch()
        
        self.scan_btn = QPushButton("Scan Files")
        controls_layout.addWidget(self.scan_btn)
        
        self.dump_btn = QPushButton("Dump Selected File")
        self.dump_btn.setEnabled(False)
        self.dump_btn.clicked.connect(self.dump_file)
        controls_layout.addWidget(self.dump_btn)

        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        controls_layout.addWidget(self.export_btn)
        
        layout.addLayout(controls_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter results...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Offset", "Name"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)

    def show_context_menu(self, position):
        """Show context menu for table."""
        menu = QMenu()
        
        scan_action = QAction("🔍 Scan with VirusTotal", self)
        scan_action.triggered.connect(self.scan_selected_file_vt)
        menu.addAction(scan_action)
        
        dump_action = QAction("💾 Dump File", self)
        dump_action.triggered.connect(self.dump_file)
        menu.addAction(dump_action)
        
        menu.exec(self.table.viewport().mapToGlobal(position))

    def scan_selected_file_vt(self):
        """Scan selected file with VirusTotal."""
        offset = self.get_selected_offset()
        if not offset:
            QMessageBox.warning(self, "Error", "Please select a file to scan.")
            return
            
        # Get main window and wrapper
        main_window = self.window()
        if not hasattr(main_window, 'vol_wrapper') or not hasattr(main_window, 'current_dump_path'):
            QMessageBox.warning(self, "Error", "Volatility wrapper not found")
            return
            
        if not main_window.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return
            
        # Check if VT API key is configured
        if not hasattr(main_window, 'virustotal_tab') or not main_window.virustotal_tab.scanner.api_key:
            reply = QMessageBox.question(
                self,
                "API Key Required",
                "VirusTotal API key is not configured. Would you like to configure it now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                main_window.tabs.setCurrentWidget(main_window.virustotal_tab)
                main_window.virustotal_tab.open_settings()
            return

        # Show progress
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog("Calculating file hash...\nThis may take a moment.", "Cancel", 0, 0, self)
        progress.setWindowTitle("Scanning File")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(False)
        progress.show()
        
        # Run in worker thread to avoid freezing
        def run_scan(*args, **kwargs):
            try:
                # 1. Calculate hash
                file_hash = main_window.vol_wrapper.calculate_file_hash(
                    main_window.current_dump_path, 
                    offset
                )
                return file_hash
            except Exception as e:
                print(f"Error in run_scan: {e}")
                return None
            
        def on_scan_complete(file_hash):
            progress.close()
            if not file_hash:
                QMessageBox.critical(self, "Error", "Failed to calculate file hash.\nCheck logs for details.")
                return
                
            # 2. Scan hash with VT
            # Switch to VT tab and add hash
            main_window.tabs.setCurrentWidget(main_window.virustotal_tab)
            main_window.virustotal_tab.add_hashes_to_table([file_hash], "File Scan")
            main_window.virustotal_tab.start_scan()
            
        # Execute
        if hasattr(main_window, 'run_worker'):
            main_window.run_worker(run_scan, on_scan_complete)
            
            # Connect cancel button
            progress.canceled.connect(lambda: None)
        else:
            # Fallback if run_worker not available (should be)
            file_hash = run_scan()
            on_scan_complete(file_hash)

    # ... (existing methods)

    def update_table(self, data):
        """Update table with file scan data."""
        self.current_data = data  # Cache data
        self.table.setRowCount(0)
        
        if not data:
            self.status_label.setText("No files found")
            return
        
        self.table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            offset = str(row_data.get('Offset', ''))
            name = str(row_data.get('Name', ''))
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(offset))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            
        self.status_label.setText(f"Loaded {len(data)} files")

    def filter_table(self, text):
        """Filter table rows based on search text."""
        search_text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def export_results(self):
        """Export current results to a file."""
        if not self.current_data:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Results", 
            "file_scan_export",
            "JSON Files (*.json);;CSV Files (*.csv);;HTML Files (*.html)"
        )
        
        if not file_path:
            return
            
        success = False
        if file_path.endswith('.json'):
            success = Exporter.export_to_json(self.current_data, file_path)
        elif file_path.endswith('.csv'):
            success = Exporter.export_to_csv(self.current_data, file_path)
        elif file_path.endswith('.html'):
            success = Exporter.export_to_html(self.current_data, file_path)
            
        if success:
            QMessageBox.information(self, "Export Success", f"Data exported to {file_path}")
        else:
            QMessageBox.critical(self, "Export Error", "Failed to export data.")

    def on_selection_changed(self):
        """Enable/disable dump button based on selection."""
        has_selection = len(self.table.selectedItems()) > 0
        self.dump_btn.setEnabled(has_selection)

    def get_selected_offset(self):
        """Get the offset of the currently selected file."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            offset_item = self.table.item(row, 0)
            if offset_item:
                return offset_item.text()
        return None



    def dump_file(self):
        """Dump the selected file."""
        offset = self.get_selected_offset()
        if not offset:
            QMessageBox.warning(self, "Error", "Please select a file to dump.")
            return
            
        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return
            
        # Call main window's dump method (assumes parent is MainWindow or has access)
        # Since FilesTab is a child of QTabWidget which is in MainWindow, we can try to access it
        # Or better, emit a signal. But for now, let's assume direct access via parent chain or passed reference
        # Actually, in MainWindow.init_tabs, we didn't pass a reference.
        # But MainWindow connects the button? No, FilesTab connects it to self.dump_file.
        # So FilesTab needs access to vol_wrapper.
        
        # Wait, in previous implementation (FilesTab.dump_file), it was accessing self.window().vol_wrapper
        # Let's check how it was implemented before.
        
        try:
            # Access MainWindow instance
            main_window = self.window()
            if hasattr(main_window, 'vol_wrapper') and hasattr(main_window, 'current_dump_path'):
                if not main_window.current_dump_path:
                    QMessageBox.warning(self, "Error", "Please load a memory dump first.")
                    return
                
                # Use main_window.run_worker to prevent freezing
                if hasattr(main_window, 'run_worker'):
                    main_window.run_worker(
                        main_window.vol_wrapper.dump_file,
                        lambda res: QMessageBox.information(self, "Success", f"File dumped to:\n{res}"),
                        main_window.current_dump_path, offset, output_dir
                    )
                else:
                    QMessageBox.warning(self, "Error", "Volatility wrapper not found")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to dump file: {str(e)}")
            self.status_label.setText("Error dumping file")
