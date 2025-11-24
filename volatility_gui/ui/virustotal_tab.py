from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QHBoxLayout, QTextEdit, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import json
from volatility_gui.logic.virustotal_api import VirusTotalAPI

class ScanThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, api, query, query_type):
        super().__init__()
        self.api = api
        self.query = query
        self.query_type = query_type

    def run(self):
        try:
            if self.query_type == "hash":
                result = self.api.scan_file_hash(self.query)
            else:
                result = self.api.scan_ip(self.query)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class VirusTotalTab(QWidget):
    def __init__(self):
        super().__init__()
        self.vt_api = VirusTotalAPI()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # API Key Input
        form_layout = QFormLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your VirusTotal API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.textChanged.connect(self.update_api_key)
        form_layout.addRow("API Key:", self.api_key_input)
        layout.addLayout(form_layout)
        
        # Scan Controls
        controls_layout = QHBoxLayout()
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Enter Hash or IP to scan")
        controls_layout.addWidget(self.scan_input)
        
        self.scan_btn = QPushButton("Scan")
        self.scan_btn.clicked.connect(self.start_scan)
        controls_layout.addWidget(self.scan_btn)
        layout.addLayout(controls_layout)
        
        # Results Area
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        layout.addWidget(self.results_area)
        
    def update_api_key(self, text):
        self.vt_api.set_api_key(text)

    def start_scan(self):
        query = self.scan_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Error", "Please enter a hash or IP.")
            return
        
        if not self.vt_api.api_key:
            QMessageBox.warning(self, "Error", "Please enter an API Key.")
            return

        # Simple heuristic to distinguish hash vs IP
        query_type = "ip" if "." in query and len(query) < 20 else "hash"
        
        self.results_area.setText(f"Scanning {query}...")
        self.scan_btn.setEnabled(False)
        
        self.thread = ScanThread(self.vt_api, query, query_type)
        self.thread.finished.connect(self.handle_result)
        self.thread.error.connect(self.handle_error)
        self.thread.start()

    def handle_result(self, result):
        self.scan_btn.setEnabled(True)
        formatted_json = json.dumps(result, indent=2)
        self.results_area.setText(formatted_json)
        
        # Parse some key info to display nicely
        if "data" in result:
            attributes = result["data"]["attributes"]
            stats = attributes.get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            
            summary = f"Malicious: {malicious} / {sum(stats.values())}\n"
            self.results_area.prepend(summary)

    def handle_error(self, error_msg):
        self.scan_btn.setEnabled(True)
        self.results_area.setText(f"Error: {error_msg}")
