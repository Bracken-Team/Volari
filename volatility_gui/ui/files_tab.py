from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt

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
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Offset", "Name"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
            name = str(row_data.get('Name', row_data.get('FileName', '')))
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(offset))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            
        self.status_label.setText(f"Found {len(data)} files")

    def dump_file(self):
        """Dump the selected file."""
        offset = self.get_selected_offset()
        if not offset:
            return

        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return
            
        try:
            self.status_label.setText(f"Dumping file at offset {offset}...")
            # Assuming main_window has passed volatility_wrapper reference or we can access it
            # Ideally, we should emit a signal, but for now let's assume direct access via parent or similar
            # Since FilesTab is instantiated in MainWindow, we can add a method to set wrapper
            
            if hasattr(self, 'vol_wrapper'):
                # We need the memory file path too. 
                # This suggests we should emit a signal to be handled by MainWindow
                pass
            else:
                # Fallback: try to find it from parent
                parent = self.window()
                if hasattr(parent, 'vol_wrapper') and hasattr(parent, 'current_dump_path'):
                    parent.vol_wrapper.dump_file(parent.current_dump_path, offset, output_dir)
                    QMessageBox.information(self, "Success", f"File dumped to {output_dir}")
                    self.status_label.setText("File dumped successfully")
                else:
                    QMessageBox.warning(self, "Error", "Volatility wrapper not found")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to dump file: {str(e)}")
            self.status_label.setText("Error dumping file")
