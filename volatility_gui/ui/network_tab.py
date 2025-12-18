from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from volatility_gui.logic.exporter import Exporter

class NetworkTab(QWidget):
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
        
        self.refresh_btn = QPushButton("Scan Network")
        controls_layout.addWidget(self.refresh_btn)
        
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Offset", "Proto", "LocalAddr", "ForeignAddr", "State"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)

    def update_table(self, data):
        """Update table with network connection data."""
        self.current_data = data  # Cache data
        self.table.setRowCount(0)
        
        if not data:
            self.status_label.setText("No network connections found")
            return
        
        self.table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            # NetScan columns: Offset, Proto, LocalAddr, LocalPort, ForeignAddr, ForeignPort, State, PID, Owner, Created
            offset = str(row_data.get('Offset', ''))
            proto = str(row_data.get('Proto', ''))
            
            # Combine address and port for display
            local_addr = str(row_data.get('LocalAddr', ''))
            local_port = str(row_data.get('LocalPort', ''))
            local = f"{local_addr}:{local_port}" if local_port else local_addr
            
            foreign_addr = str(row_data.get('ForeignAddr', ''))
            foreign_port = str(row_data.get('ForeignPort', ''))
            foreign = f"{foreign_addr}:{foreign_port}" if foreign_port else foreign_addr
            
            state = str(row_data.get('State', ''))
            
            offset_item = QTableWidgetItem(offset)
            offset_item.setToolTip(offset)
            self.table.setItem(row_idx, 0, offset_item)
            
            proto_item = QTableWidgetItem(proto)
            proto_item.setToolTip(proto)
            self.table.setItem(row_idx, 1, proto_item)
            
            local_item = QTableWidgetItem(local)
            local_item.setToolTip(local)
            self.table.setItem(row_idx, 2, local_item)
            
            foreign_item = QTableWidgetItem(foreign)
            foreign_item.setToolTip(foreign)
            self.table.setItem(row_idx, 3, foreign_item)
            
            state_item = QTableWidgetItem(state)
            state_item.setToolTip(state)
            self.table.setItem(row_idx, 4, state_item)
            
        self.status_label.setText(f"Loaded {len(data)} network connections")

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
            "network_scan_export",
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
