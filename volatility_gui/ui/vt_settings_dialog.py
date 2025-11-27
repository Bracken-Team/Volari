from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt
from volatility_gui.logic.virustotal_scanner import VirusTotalScanner


class VTSettingsDialog(QDialog):
    """Dialog for configuring VirusTotal API settings."""
    
    def __init__(self, scanner: VirusTotalScanner, parent=None):
        super().__init__(parent)
        self.scanner = scanner
        self.setWindowTitle("VirusTotal Settings")
        self.setMinimumWidth(500)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # API Key Section
        api_group = QGroupBox("API Key Configuration")
        api_layout = QFormLayout()
        
        # Info label
        info_label = QLabel(
            "Enter your VirusTotal API key. You can get a free API key by signing up at:\n"
            "https://www.virustotal.com/gui/join-us"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        api_layout.addRow(info_label)
        
        # API key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your VirusTotal API key...")
        
        # Load existing key if available
        if self.scanner.api_key:
            self.api_key_input.setText(self.scanner.api_key)
            
        api_layout.addRow("API Key:", self.api_key_input)
        
        # Show/Hide button
        show_hide_layout = QHBoxLayout()
        self.show_key_btn = QPushButton("👁 Show")
        self.show_key_btn.setMaximumWidth(80)
        self.show_key_btn.clicked.connect(self.toggle_key_visibility)
        show_hide_layout.addWidget(self.show_key_btn)
        show_hide_layout.addStretch()
        api_layout.addRow("", show_hide_layout)
        
        # Test button
        self.test_btn = QPushButton("🔍 Test API Key")
        self.test_btn.clicked.connect(self.test_api_key)
        api_layout.addRow("", self.test_btn)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        api_layout.addRow("Status:", self.status_label)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Cache Section
        cache_group = QGroupBox("Cache Management")
        cache_layout = QFormLayout()
        
        # Cache stats
        stats = self.scanner.get_cache_stats()
        self.cache_stats_label = QLabel(
            f"Total cached: {stats['total_cached']} | "
            f"Malicious: {stats['malicious']} | "
            f"Clean: {stats['clean']}"
        )
        cache_layout.addRow("Cache Stats:", self.cache_stats_label)
        
        # Clear cache button
        clear_cache_btn = QPushButton("🗑 Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        cache_layout.addRow("", clear_cache_btn)
        
        cache_group.setLayout(cache_layout)
        layout.addWidget(cache_group)
        
        # Rate Limit Info
        rate_group = QGroupBox("Rate Limit Information")
        rate_layout = QVBoxLayout()
        rate_info = QLabel(
            "Free API Tier Limits:\n"
            "• 4 requests per minute\n"
            "• 500 requests per day\n"
            "• 15,500 requests per month\n\n"
            "The scanner automatically respects these limits."
        )
        rate_info.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        rate_layout.addWidget(rate_info)
        rate_group.setLayout(rate_layout)
        layout.addWidget(rate_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def toggle_key_visibility(self):
        """Toggle API key visibility."""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("🔒 Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("👁 Show")
            
    def test_api_key(self):
        """Test the API key."""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            self.status_label.setText("❌ Please enter an API key")
            self.status_label.setStyleSheet("color: #d32f2f;")
            return
            
        self.status_label.setText("⏳ Testing API key...")
        self.status_label.setStyleSheet("color: #1976D2;")
        self.test_btn.setEnabled(False)
        
        # Test in a separate thread would be better, but for now:
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self._do_test(api_key))
        
    def _do_test(self, api_key):
        """Actually perform the test."""
        if self.scanner.set_api_key(api_key):
            self.status_label.setText("✅ API key is valid!")
            self.status_label.setStyleSheet("color: #388E3C;")
            QMessageBox.information(
                self,
                "Success",
                "API key validated successfully!\n\n"
                "You can now scan hashes with VirusTotal."
            )
        else:
            self.status_label.setText("❌ Invalid API key")
            self.status_label.setStyleSheet("color: #d32f2f;")
            QMessageBox.warning(
                self,
                "Invalid API Key",
                "The API key could not be validated.\n\n"
                "Please check that you entered it correctly."
            )
            
        self.test_btn.setEnabled(True)
        
    def clear_cache(self):
        """Clear the VT cache."""
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "Are you sure you want to clear all cached VirusTotal results?\n\n"
            "This will require re-scanning hashes on next use.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scanner.clear_cache()
            stats = self.scanner.get_cache_stats()
            self.cache_stats_label.setText(
                f"Total cached: {stats['total_cached']} | "
                f"Malicious: {stats['malicious']} | "
                f"Clean: {stats['clean']}"
            )
            QMessageBox.information(self, "Success", "Cache cleared successfully!")
            
    def save_settings(self):
        """Save the settings."""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(
                self,
                "No API Key",
                "Please enter an API key before saving."
            )
            return
            
        # Set the API key (will validate)
        if self.scanner.set_api_key(api_key):
            QMessageBox.information(
                self,
                "Success",
                "Settings saved successfully!"
            )
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Invalid API Key",
                "The API key could not be validated.\n\n"
                "Please test the key before saving."
            )
