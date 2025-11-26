from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QTextEdit, QCheckBox, QPushButton, QFileDialog, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt


class ReportConfigDialog(QDialog):
    """Dialog to configure PDF report generation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate PDF Report")
        self.resize(500, 600)
        
        self.config = {
            'case_name': 'Forensic Analysis Report',
            'analyst': '',
            'notes': '',
            'output_path': '',
            'include_system_info': True,
            'include_processes': True,
            'include_network': True,
            'include_registry': True,
            'include_files': True
        }
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Case Information
        case_group = QGroupBox("Case Information")
        case_layout = QVBoxLayout()
        
        # Case Name
        case_name_layout = QHBoxLayout()
        case_name_layout.addWidget(QLabel("Case Name:"))
        self.case_name_input = QLineEdit(self.config['case_name'])
        case_name_layout.addWidget(self.case_name_input)
        case_layout.addLayout(case_name_layout)
        
        # Analyst
        analyst_layout = QHBoxLayout()
        analyst_layout.addWidget(QLabel("Analyst:"))
        self.analyst_input = QLineEdit()
        analyst_layout.addWidget(self.analyst_input)
        case_layout.addLayout(analyst_layout)
        
        # Notes
        case_layout.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter any additional notes or observations...")
        self.notes_input.setMaximumHeight(100)
        case_layout.addWidget(self.notes_input)
        
        case_group.setLayout(case_layout)
        layout.addWidget(case_group)
        
        # Sections to Include
        sections_group = QGroupBox("Sections to Include")
        sections_layout = QVBoxLayout()
        
        self.system_info_check = QCheckBox("System Information")
        self.system_info_check.setChecked(True)
        sections_layout.addWidget(self.system_info_check)
        
        self.processes_check = QCheckBox("Process List")
        self.processes_check.setChecked(True)
        sections_layout.addWidget(self.processes_check)
        
        self.network_check = QCheckBox("Network Connections")
        self.network_check.setChecked(True)
        sections_layout.addWidget(self.network_check)
        
        self.registry_check = QCheckBox("Registry Hives")
        self.registry_check.setChecked(True)
        sections_layout.addWidget(self.registry_check)
        
        self.files_check = QCheckBox("File Scan Results")
        self.files_check.setChecked(True)
        sections_layout.addWidget(self.files_check)
        
        sections_group.setLayout(sections_layout)
        layout.addWidget(sections_group)
        
        # Output Path
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Save to:"))
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Select output path...")
        path_layout.addWidget(self.output_path_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output)
        path_layout.addWidget(browse_btn)
        
        output_layout.addLayout(path_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        generate_btn = QPushButton("Generate Report")
        generate_btn.clicked.connect(self.accept)
        button_layout.addWidget(generate_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def browse_output(self):
        """Browse for output file path."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            "forensic_report.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'
            self.output_path_input.setText(file_path)
            
    def get_config(self):
        """Get the configuration from the dialog."""
        self.config['case_name'] = self.case_name_input.text() or 'Forensic Analysis Report'
        self.config['analyst'] = self.analyst_input.text()
        self.config['notes'] = self.notes_input.toPlainText()
        self.config['output_path'] = self.output_path_input.text()
        self.config['include_system_info'] = self.system_info_check.isChecked()
        self.config['include_processes'] = self.processes_check.isChecked()
        self.config['include_network'] = self.network_check.isChecked()
        self.config['include_registry'] = self.registry_check.isChecked()
        self.config['include_files'] = self.files_check.isChecked()
        
        return self.config
        
    def accept(self):
        """Validate and accept the dialog."""
        if not self.output_path_input.text():
            QMessageBox.warning(self, "Missing Information", "Please select an output path for the report.")
            return
            
        # Check if at least one section is selected
        if not any([
            self.system_info_check.isChecked(),
            self.processes_check.isChecked(),
            self.network_check.isChecked(),
            self.registry_check.isChecked(),
            self.files_check.isChecked()
        ]):
            QMessageBox.warning(self, "No Sections Selected", "Please select at least one section to include in the report.")
            return
            
        super().accept()
