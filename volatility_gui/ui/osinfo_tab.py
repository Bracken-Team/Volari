from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout, 
                             QLabel, QScrollArea, QGroupBox, QFormLayout, QGridLayout, QFrame, QSizePolicy, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class OSInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. Controls area (Header)
        controls_layout = QHBoxLayout()
        self.status_label = QLabel("Ready to analyze")
        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch()
        
        self.refresh_btn = QPushButton("Get OS Info")
        controls_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # 2. Main Content Area (Scrollable Dashboard)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.dashboard_widget = QWidget()
        self.dashboard_layout = QGridLayout(self.dashboard_widget)
        self.dashboard_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.dashboard_layout.setSpacing(20)
        
        scroll.setWidget(self.dashboard_widget)
        layout.addWidget(scroll)
        
        # Initialize groups (hidden until data loaded)
        self.groups = {}

    def create_group(self, title, items, row, col):
        """Create a styled group box with key-value pairs."""
        group = QGroupBox(title)
        # Use Tokyo Night themed border color
        group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #414868; border-radius: 8px; margin-top: 10px; padding-top: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #7aa2f7; }")
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        for key, value in items:
            key_label = QLabel(f"{key}:")
            # Remove hardcoded color, rely on system theme
            key_label.setStyleSheet("font-weight: bold;")
            
            # Use QLabel with word wrap instead of QLineEdit to prevent cutoff
            val_str = str(value)
            value_label = QLabel(val_str)
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value_label.setToolTip(val_str)
            
            layout.addRow(key_label, value_label)
            
        group.setLayout(layout)
        self.dashboard_layout.addWidget(group, row, col)
        return group

    def update_display(self, data):
        """Update the dashboard with organized OS information."""
        if not data:
            self.status_label.setText("No OS information found")
            return
            
        # Clear existing layout items
        while self.dashboard_layout.count():
            item = self.dashboard_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Consolidate list of dicts into one dict
        info = {}
        # Debug: Print first row to understand structure
        if data:
            print(f"DEBUG: First row data: {data[0]}")
        
        for row in data:
            if isinstance(row, dict):
                # Check for standard Key/Value or Variable/Value structure typical of windows.info
                # windows.info typically has columns ["Variable", "Value"]
                if "Variable" in row and "Value" in row:
                    key = str(row["Variable"]).strip()
                    val = row["Value"]
                    info[key] = val
                elif "Member" in row and "Value" in row:
                    key = str(row["Member"]).strip()
                    val = row["Value"]
                    info[key] = val
                else:
                    # Fallback for columns-as-keys format (single row or standard table)
                    for key, value in row.items():
                        clean_key = str(key).strip()
                        info[clean_key] = value
            else:
                # Handle non-dict items if any
                print(f"WARNING: Unexpected row type: {type(row)} - {row}")

        # If info is empty after processing, show warning
        if not info:
             self.status_label.setText("Error: Data format unexpected")
             return

        # Categorize Data
        # Note: Added more specific keys commonly seen in windows.info
        system_keys = ["NTBuild", "Major", "Minor", "Platform", "ServicePack", "KdCopyDataBlock", "System Root", "Strict"]
        time_keys = ["SystemTime", "BootTime", "TimeDateStamp", "PE TimeDateStamp"] 
        kernel_keys = ["KernelBase", "KDBG", "KPCR", "Prcb", "Idt", "Gdt", "TSS", "DTB"]
        config_keys = ["LayerName", "SymbolTable", "Is64Bit", "Symbols"]
        
        # Build Groups
        system_data = []
        time_data = []
        kernel_data = []
        config_data = []
        other_data = []
        
        for key, value in info.items():
            # Clean key for matching (remove spaces, lower case check maybe?)
            k_clean = key.replace(" ", "") 
            
            # Categorization Logic
            if any(x in k_clean for x in system_keys) or "Version" in key:
                system_data.append((key, value))
            elif any(x in k_clean for x in time_keys):
                time_data.append((key, value))
            elif any(x in k_clean for x in kernel_keys):
                kernel_data.append((key, value))
            elif any(x in k_clean for x in config_keys):
                config_data.append((key, value))
            else:
                other_data.append((key, value))
                
        # Create Widgets
        row = 0
        if system_data:
            self.create_group("System Version", system_data, row, 0)
        
        if time_data:
            self.create_group("Time Information", time_data, row, 1)
            
        row += 1
        if kernel_data:
            self.create_group("Kernel Core", kernel_data, row, 0)
            
        if config_data:
            self.create_group("Configuration & Paths", config_data, row, 1)
            
        row += 1
        if other_data:
            # Span 'Other' across full width if it's the last one
            group = self.create_group("Additional Information", other_data, row, 0)
            self.dashboard_layout.addWidget(group, row, 0, 1, 2)
        
        # Update button text to "Refresh" since we have data
        self.refresh_btn.setText("Refresh")
        self.status_label.setText(f"OS details loaded ({len(info)} properties)")
