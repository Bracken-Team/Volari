from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel, QFileDialog, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt
import os

class FilesTab(QWidget):
    def __init__(self):
        super().__init__()
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
        
        layout.addWidget(self.table)

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

    def update_table(self, data):
        """Update table with file scan data."""
        self.table.setRowCount(0)
        
        if not data:
            self.status_label.setText("No files found")
            return
        
        # Set correct columns for filescan
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Offset", "Name"])
        
        self.table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            offset = str(row_data.get('Offset', ''))
            name = str(row_data.get('Name', ''))
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(offset))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            
        self.status_label.setText(f"Loaded {len(data)} files")

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
