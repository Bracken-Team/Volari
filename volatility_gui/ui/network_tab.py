from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt

class NetworkTab(QWidget):
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
        
        self.refresh_btn = QPushButton("Scan Network")
        controls_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Offset", "Proto", "LocalAddr", "ForeignAddr", "State"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)

    def update_table(self, data):
        self.table.setRowCount(0)
        self.table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            offset = str(row_data.get('Offset', ''))
            proto = str(row_data.get('Proto', ''))
            local = str(row_data.get('LocalAddr', ''))
            foreign = str(row_data.get('ForeignAddr', ''))
            state = str(row_data.get('State', ''))
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(offset))
            self.table.setItem(row_idx, 1, QTableWidgetItem(proto))
            self.table.setItem(row_idx, 2, QTableWidgetItem(local))
            self.table.setItem(row_idx, 3, QTableWidgetItem(foreign))
            self.table.setItem(row_idx, 4, QTableWidgetItem(state))
            
        self.status_label.setText(f"Showing {len(data)} connections")
