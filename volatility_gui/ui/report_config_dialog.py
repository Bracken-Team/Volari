from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QTextEdit, QCheckBox, QPushButton, QFileDialog, QGroupBox, QMessageBox,
                             QGridLayout, QFrame)
from PyQt6.QtCore import Qt


class ReportConfigDialog(QDialog):
    """Dialog to configure PDF report generation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate PDF Report")
        self.resize(480, 520)
        self.setModal(True)
        
        # Tokyo Night theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1b26;
                color: #c0caf5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #414868;
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px;
                background-color: #24283b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
                color: #7aa2f7;
            }
            QLabel {
                color: #a9b1d6;
                background: transparent;
            }
            QLineEdit, QTextEdit {
                background-color: #1a1b26;
                color: #c0caf5;
                border: 1px solid #414868;
                border-radius: 6px;
                padding: 8px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #7aa2f7;
            }
            QCheckBox {
                color: #c0caf5;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #414868;
                background-color: #1a1b26;
            }
            QCheckBox::indicator:checked {
                background-color: #7aa2f7;
                border-color: #7aa2f7;
            }
            QPushButton {
                background-color: #414868;
                color: #c0caf5;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #565f89;
            }
            QPushButton#generateBtn {
                background-color: #7aa2f7;
                color: #1a1b26;
            }
            QPushButton#generateBtn:hover {
                background-color: #89b4ff;
            }
        """)
        
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
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Case Information
        case_group = QGroupBox("Case Information")
        case_layout = QVBoxLayout()
        case_layout.setSpacing(8)
        
        # Case Name row
        self.case_name_input = QLineEdit(self.config['case_name'])
        self.case_name_input.setPlaceholderText("Enter case name...")
        case_layout.addWidget(QLabel("Case Name"))
        case_layout.addWidget(self.case_name_input)
        
        # Analyst row
        self.analyst_input = QLineEdit()
        self.analyst_input.setPlaceholderText("Enter analyst name...")
        case_layout.addWidget(QLabel("Analyst"))
        case_layout.addWidget(self.analyst_input)
        
        # Notes
        notes_label = QLabel("Notes")
        case_layout.addWidget(notes_label)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter any additional notes or observations...")
        self.notes_input.setMaximumHeight(80)
        case_layout.addWidget(self.notes_input)
        
        case_group.setLayout(case_layout)
        layout.addWidget(case_group)
        
        # Sections to Include (grid layout for compactness)
        sections_group = QGroupBox("Include in Report")
        sections_layout = QGridLayout()
        sections_layout.setSpacing(12)
        
        self.system_info_check = QCheckBox("System Info")
        self.system_info_check.setChecked(True)
        sections_layout.addWidget(self.system_info_check, 0, 0)
        
        self.processes_check = QCheckBox("Processes")
        self.processes_check.setChecked(True)
        sections_layout.addWidget(self.processes_check, 0, 1)
        
        self.network_check = QCheckBox("Network")
        self.network_check.setChecked(True)
        sections_layout.addWidget(self.network_check, 1, 0)
        
        self.registry_check = QCheckBox("Registry")
        self.registry_check.setChecked(True)
        sections_layout.addWidget(self.registry_check, 1, 1)
        
        self.files_check = QCheckBox("File Scan")
        self.files_check.setChecked(True)
        sections_layout.addWidget(self.files_check, 2, 0)
        
        sections_group.setLayout(sections_layout)
        layout.addWidget(sections_group)
        
        # Output Path
        output_group = QGroupBox("Output Location")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(8)
        
        output_layout.addWidget(QLabel("Save Report To"))
        
        path_layout = QHBoxLayout()
        path_layout.setSpacing(8)
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Select output path...")
        path_layout.addWidget(self.output_path_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self.browse_output)
        path_layout.addWidget(browse_btn)
        
        output_layout.addLayout(path_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        generate_btn = QPushButton("Generate Report")
        generate_btn.setObjectName("generateBtn")
        generate_btn.clicked.connect(self.accept)
        button_layout.addWidget(generate_btn)
        
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

