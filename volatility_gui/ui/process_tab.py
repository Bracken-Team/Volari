from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt

class ProcessTab(QWidget):
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
        
        self.refresh_btn = QPushButton("Refresh Process List")
        # self.refresh_btn.clicked.connect(self.refresh_data) # To be connected by main window
        controls_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["PID", "PPID", "ImageFileName", "Offset", "Threads", "Handles"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)

    def update_table(self, data):
        """
        Updates the table with a list of dictionaries.
        Expected keys: PID, PPID, ImageFileName, Offset, Threads, Handles
        """
        self.table.setRowCount(0)
        self.table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            # Map keys to columns. Adjust keys based on actual Volatility output
            # Common keys: 'PID', 'PPID', 'ImageFileName', 'Offset', 'Threads', 'Handles'
            
            pid = str(row_data.get('PID', ''))
            ppid = str(row_data.get('PPID', ''))
            name = str(row_data.get('ImageFileName', ''))
            offset = str(row_data.get('Offset', ''))
            threads = str(row_data.get('Threads', ''))
            handles = str(row_data.get('Handles', ''))
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(pid))
            self.table.setItem(row_idx, 1, QTableWidgetItem(ppid))
            self.table.setItem(row_idx, 2, QTableWidgetItem(name))
            self.table.setItem(row_idx, 3, QTableWidgetItem(offset))
            self.table.setItem(row_idx, 4, QTableWidgetItem(threads))
            self.table.setItem(row_idx, 5, QTableWidgetItem(handles))
            
        self.status_label.setText(f"Showing {len(data)} processes")
