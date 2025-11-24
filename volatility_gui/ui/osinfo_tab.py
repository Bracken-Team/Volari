from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton, 
                             QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt

class OSInfoTab(QWidget):
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
        
        self.refresh_btn = QPushButton("Get OS Info")
        controls_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Text display for OS information
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace;")
        
        layout.addWidget(self.info_display)

    def update_display(self, data):
        """Update the display with OS information."""
        if not data:
            self.status_label.setText("No OS information found")
            return
        
        # Format the data as key-value pairs
        text = "=== System Information ===\n\n"
        
        for row in data:
            for key, value in row.items():
                text += f"{key:30s}: {value}\n"
            text += "\n"
        
        self.info_display.setPlainText(text)
        self.status_label.setText("OS information loaded")
