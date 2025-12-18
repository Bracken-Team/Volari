from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QGroupBox, QFileDialog, QMessageBox, QComboBox, QLineEdit, QDialog)
from PyQt6.QtCore import Qt
from volatility_gui.logic.ioc_scanner import IOCScanner
from volatility_gui.logic.exporter import Exporter

class IOCTab(QWidget):
    """Tab for IOC scanning and management."""
    
    def __init__(self):
        super().__init__()
        self.scanner = IOCScanner()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Input Area
        input_group = QGroupBox("IOC Management")
        input_layout = QVBoxLayout()
        
        # Text area for manual entry
        self.ioc_input = QTextEdit()
        self.ioc_input.setPlaceholderText("Enter IOCs here (one per line)...\nExample:\n192.168.1.100\nmalicious-domain.com\n5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8")
        self.ioc_input.setMaximumHeight(100)
        input_layout.addWidget(self.ioc_input)
        
        # Controls for input
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add IOCs")
        self.add_btn.clicked.connect(self.add_manual_iocs)
        btn_layout.addWidget(self.add_btn)
        
        self.load_btn = QPushButton("Load from File")
        self.load_btn.clicked.connect(self.load_iocs_from_file)
        btn_layout.addWidget(self.load_btn)
        
        self.clear_btn = QPushButton("Clear IOCs")
        self.clear_btn.clicked.connect(self.clear_iocs)
        btn_layout.addWidget(self.clear_btn)
        
        self.view_btn = QPushButton("View Keywords")
        self.view_btn.clicked.connect(self.view_keywords)
        btn_layout.addWidget(self.view_btn)
        
        btn_layout.addStretch()
        
        self.ioc_count_label = QLabel("Active IOCs: 0")
        btn_layout.addWidget(self.ioc_count_label)
        
        input_layout.addLayout(btn_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Scan Controls
        scan_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Run Scan")
        self.scan_btn.clicked.connect(self.run_scan)
        self.scan_btn.setStyleSheet("font-weight: bold; padding: 5px 15px;")
        scan_layout.addWidget(self.scan_btn)
        
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        scan_layout.addWidget(self.export_btn)
        
        scan_layout.addStretch()
        layout.addLayout(scan_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search Results:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter matches...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Type", "IOC Value", "Found In", "Context", "Field"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        
        self.status_label = QLabel("Ready to scan")
        layout.addWidget(self.status_label)
        
    def add_manual_iocs(self):
        """Add IOCs from the text area."""
        text = self.ioc_input.toPlainText()
        if not text:
            return
            
        count = 0
        for line in text.split('\n'):
            line = line.strip()
            if line:
                self.scanner.add_ioc(line)
                count += 1
                
        self.ioc_input.clear()
        self.update_ioc_count()
        self.status_label.setText(f"Added {count} IOCs")
        
    def load_iocs_from_file(self):
        """Load IOCs from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load IOCs", "", "IOC Files (*.json *.csv *.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                self.scanner.load_from_file(file_path)
                self.update_ioc_count()
                self.status_label.setText(f"Loaded IOCs from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load IOCs: {str(e)}")
                
    def clear_iocs(self):
        """Clear all IOCs."""
        self.scanner.clear_iocs()
        self.update_ioc_count()
        self.status_label.setText("IOCs cleared")
        
    def update_ioc_count(self):
        """Update the IOC count label."""
        total = sum(len(s) for s in self.scanner.iocs.values())
        details = [f"{k}: {len(v)}" for k, v in self.scanner.iocs.items() if v]
        detail_str = f" ({', '.join(details)})" if details else ""
        self.ioc_count_label.setText(f"Active IOCs: {total}{detail_str}")

    def view_keywords(self):
        """View all active IOC keywords."""
        if not any(self.scanner.iocs.values()):
            QMessageBox.information(self, "IOC Keywords", "No IOCs added yet.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Active IOC Keywords")
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        content = ""
        for ioc_type, iocs in self.scanner.iocs.items():
            if iocs:
                content += f"=== {ioc_type} ===\n"
                for ioc in sorted(iocs):
                    content += f"{ioc}\n"
                content += "\n"
        
        text_edit.setPlainText(content)
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()

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
        
    def run_scan(self):
        """Run the scan against loaded data."""
        # This will be connected to MainWindow to get data
        pass
        
    def display_results(self, matches):
        """Display scan results in the table."""
        self.table.setRowCount(0)
        
        if not matches:
            self.status_label.setText("Scan complete. No matches found.")
            return
            
        self.table.setRowCount(len(matches))
        for i, match in enumerate(matches):
            self.table.setItem(i, 0, QTableWidgetItem(match['Type']))
            self.table.setItem(i, 1, QTableWidgetItem(match['Value']))
            self.table.setItem(i, 2, QTableWidgetItem(match['Source']))
            self.table.setItem(i, 3, QTableWidgetItem(match['Context']))
            self.table.setItem(i, 4, QTableWidgetItem(match['Field']))
            
        self.status_label.setText(f"Scan complete. Found {len(matches)} matches.")
        
    def export_results(self):
        """Export scan results."""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Export Error", "No results to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "ioc_scan_results",
            "JSON Files (*.json);;CSV Files (*.csv);;HTML Files (*.html)"
        )
        
        if not file_path:
            return
            
        # Collect data from table
        data = []
        for row in range(self.table.rowCount()):
            item = {
                "Type": self.table.item(row, 0).text(),
                "Value": self.table.item(row, 1).text(),
                "Source": self.table.item(row, 2).text(),
                "Context": self.table.item(row, 3).text(),
                "Field": self.table.item(row, 4).text()
            }
            data.append(item)
            
        if file_path.endswith('.json'):
            Exporter.export_to_json(data, file_path)
        elif file_path.endswith('.csv'):
            Exporter.export_to_csv(data, file_path)
        elif file_path.endswith('.html'):
            Exporter.export_to_html(data, file_path, "IOC Scan Results")
            
        QMessageBox.information(self, "Success", f"Results exported to {file_path}")
