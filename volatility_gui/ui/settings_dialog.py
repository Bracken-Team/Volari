from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
                             QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox,
                             QCheckBox, QFileDialog, QGroupBox, QFormLayout, QListWidget,
                             QMessageBox, QTextEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt
from pathlib import Path
from typing import Optional

from volatility_gui.logic.settings_manager import SettingsManager
from volatility_gui.logic.virustotal_scanner import VirusTotalScanner


class SettingsDialog(QDialog):
    """Comprehensive settings dialog with multiple tabs."""
    
    def __init__(self, settings_manager: SettingsManager, vt_scanner: Optional[VirusTotalScanner] = None, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.vt_scanner = vt_scanner
        
        self.setWindowTitle("Settings")
        self.resize(700, 600)
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the UI with tabs."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.tabs.addTab(self.create_application_tab(), "Application")
        self.tabs.addTab(self.create_virustotal_tab(), "VirusTotal")
        self.tabs.addTab(self.create_volatility_tab(), "Volatility")
        self.tabs.addTab(self.create_report_tab(), "Report")
        self.tabs.addTab(self.create_performance_tab(), "Performance")
        self.tabs.addTab(self.create_advanced_tab(), "Advanced")
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)
        layout.addWidget(button_box)
        
    def create_application_tab(self) -> QWidget:
        """Create Application Preferences tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        layout.addRow("Theme:", self.theme_combo)
        
        # Auto-save
        self.auto_save_check = QCheckBox("Automatically save analysis results")
        layout.addRow("Auto-save:", self.auto_save_check)
        
        # Default export format
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["csv", "json", "html"])
        layout.addRow("Default Export Format:", self.export_format_combo)
        
        # Max concurrent tasks
        self.max_tasks_spin = QSpinBox()
        self.max_tasks_spin.setRange(1, 10)
        self.max_tasks_spin.setToolTip("Number of plugins that can run simultaneously")
        layout.addRow("Max Concurrent Tasks:", self.max_tasks_spin)
        
        layout.addRow(QLabel(""))  # Spacer
        layout.addRow(QLabel("<i>Note: Theme changes require restart</i>"))
        
        return widget
        
    def create_virustotal_tab(self) -> QWidget:
        """Create VirusTotal Settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API Key group
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()
        
        self.vt_api_key_input = QLineEdit()
        self.vt_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.vt_api_key_input.setPlaceholderText("Enter your VirusTotal API key")
        api_layout.addRow("API Key:", self.vt_api_key_input)
        
        test_btn = QPushButton("Test API Key")
        test_btn.clicked.connect(self.test_vt_api_key)
        api_layout.addRow("", test_btn)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Cache group
        cache_group = QGroupBox("Cache Settings")
        cache_layout = QFormLayout()
        
        self.vt_cache_enabled = QCheckBox("Enable result caching")
        cache_layout.addRow("Cache:", self.vt_cache_enabled)
        
        self.vt_rate_limit_spin = QSpinBox()
        self.vt_rate_limit_spin.setRange(1, 1000)
        self.vt_rate_limit_spin.setToolTip("Requests per minute (free tier: 4)")
        cache_layout.addRow("Rate Limit:", self.vt_rate_limit_spin)
        
        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_vt_cache)
        cache_layout.addRow("", clear_cache_btn)
        
        cache_group.setLayout(cache_layout)
        layout.addWidget(cache_group)
        
        layout.addStretch()
        return widget
        
    def create_volatility_tab(self) -> QWidget:
        """Create Volatility Configuration tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Symbol path
        symbol_layout = QHBoxLayout()
        self.symbol_path_input = QLineEdit()
        self.symbol_path_input.setPlaceholderText("Path to symbol server")
        symbol_layout.addWidget(self.symbol_path_input)
        symbol_browse_btn = QPushButton("Browse...")
        symbol_browse_btn.clicked.connect(lambda: self.browse_directory(self.symbol_path_input))
        symbol_layout.addWidget(symbol_browse_btn)
        layout.addRow("Symbol Path:", symbol_layout)
        
        # Plugin paths
        layout.addRow(QLabel("Plugin Paths:"))
        self.plugin_paths_list = QListWidget()
        self.plugin_paths_list.setMaximumHeight(100)
        layout.addRow(self.plugin_paths_list)
        
        plugin_btn_layout = QHBoxLayout()
        add_plugin_btn = QPushButton("Add Path")
        add_plugin_btn.clicked.connect(self.add_plugin_path)
        plugin_btn_layout.addWidget(add_plugin_btn)
        remove_plugin_btn = QPushButton("Remove Path")
        remove_plugin_btn.clicked.connect(self.remove_plugin_path)
        plugin_btn_layout.addWidget(remove_plugin_btn)
        plugin_btn_layout.addStretch()
        layout.addRow(plugin_btn_layout)
        
        # Cache directory
        cache_layout = QHBoxLayout()
        self.cache_dir_input = QLineEdit()
        self.cache_dir_input.setPlaceholderText("~/.volatility3/cache")
        cache_layout.addWidget(self.cache_dir_input)
        cache_browse_btn = QPushButton("Browse...")
        cache_browse_btn.clicked.connect(lambda: self.browse_directory(self.cache_dir_input))
        cache_layout.addWidget(cache_browse_btn)
        layout.addRow("Cache Directory:", cache_layout)
        
        # ISF path
        isf_layout = QHBoxLayout()
        self.isf_path_input = QLineEdit()
        self.isf_path_input.setPlaceholderText("Path to ISF files")
        isf_layout.addWidget(self.isf_path_input)
        isf_browse_btn = QPushButton("Browse...")
        isf_browse_btn.clicked.connect(lambda: self.browse_directory(self.isf_path_input))
        isf_layout.addWidget(isf_browse_btn)
        layout.addRow("ISF Path:", isf_layout)
        
        return widget
        
    def create_report_tab(self) -> QWidget:
        """Create Report Settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Analyst name
        self.analyst_name_input = QLineEdit()
        self.analyst_name_input.setPlaceholderText("Your name")
        layout.addRow("Analyst Name:", self.analyst_name_input)
        
        # Company
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("Organization name")
        layout.addRow("Company/Organization:", self.company_input)
        
        # Logo path
        logo_layout = QHBoxLayout()
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setPlaceholderText("Path to company logo (PNG/JPG)")
        logo_layout.addWidget(self.logo_path_input)
        logo_browse_btn = QPushButton("Browse...")
        logo_browse_btn.clicked.connect(lambda: self.browse_file(self.logo_path_input, "Images (*.png *.jpg *.jpeg)"))
        logo_layout.addWidget(logo_browse_btn)
        layout.addRow("Logo Path:", logo_layout)
        
        # Template
        self.template_combo = QComboBox()
        self.template_combo.addItems(["default", "detailed", "executive"])
        layout.addRow("Report Template:", self.template_combo)
        
        layout.addRow(QLabel(""))  # Spacer
        layout.addRow(QLabel("<i>These values will pre-fill report generation dialogs</i>"))
        
        return widget
        
    def create_performance_tab(self) -> QWidget:
        """Create Performance Settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Memory limit
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(512, 32768)
        self.memory_limit_spin.setSingleStep(512)
        self.memory_limit_spin.setSuffix(" MB")
        self.memory_limit_spin.setToolTip("Maximum memory usage for analysis")
        layout.addRow("Memory Limit:", self.memory_limit_spin)
        
        # Worker threads
        self.worker_threads_spin = QSpinBox()
        self.worker_threads_spin.setRange(1, 16)
        self.worker_threads_spin.setToolTip("Number of background worker threads")
        layout.addRow("Worker Threads:", self.worker_threads_spin)
        
        # Cache size
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(64, 4096)
        self.cache_size_spin.setSingleStep(64)
        self.cache_size_spin.setSuffix(" MB")
        self.cache_size_spin.setToolTip("Maximum cache size for results")
        layout.addRow("Cache Size:", self.cache_size_spin)
        
        layout.addRow(QLabel(""))  # Spacer
        layout.addRow(QLabel("<i>Higher values improve performance but use more resources</i>"))
        
        return widget
        
    def create_advanced_tab(self) -> QWidget:
        """Create Advanced Settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Debug mode
        self.debug_mode_check = QCheckBox("Enable debug mode (verbose logging)")
        layout.addWidget(self.debug_mode_check)
        
        # Plugin timeout
        timeout_layout = QFormLayout()
        self.plugin_timeout_spin = QSpinBox()
        self.plugin_timeout_spin.setRange(10, 3600)
        self.plugin_timeout_spin.setSuffix(" seconds")
        self.plugin_timeout_spin.setToolTip("Maximum time for plugin execution")
        timeout_layout.addRow("Plugin Timeout:", self.plugin_timeout_spin)
        layout.addLayout(timeout_layout)
        
        # Auto-investigation plugins
        layout.addWidget(QLabel("Auto-Investigation Plugins:"))
        self.auto_plugins_text = QTextEdit()
        self.auto_plugins_text.setMaximumHeight(150)
        self.auto_plugins_text.setPlaceholderText("One plugin per line (e.g., windows.pslist.PsList)")
        layout.addWidget(self.auto_plugins_text)
        
        layout.addWidget(QLabel("<i>Advanced settings - modify with caution</i>"))
        layout.addStretch()
        
        return widget
        
    def load_settings(self):
        """Load current settings into UI."""
        # Application
        self.theme_combo.setCurrentText(self.settings.get("application.theme", "light"))
        self.auto_save_check.setChecked(self.settings.get("application.auto_save", True))
        self.export_format_combo.setCurrentText(self.settings.get("application.default_export_format", "csv"))
        self.max_tasks_spin.setValue(self.settings.get("application.max_concurrent_tasks", 1))
        
        # VirusTotal
        self.vt_api_key_input.setText(self.settings.get("virustotal.api_key", ""))
        self.vt_cache_enabled.setChecked(self.settings.get("virustotal.cache_enabled", True))
        self.vt_rate_limit_spin.setValue(self.settings.get("virustotal.rate_limit", 4))
        
        # Volatility
        self.symbol_path_input.setText(self.settings.get("volatility.symbol_path", ""))
        plugin_paths = self.settings.get("volatility.plugin_paths", [])
        self.plugin_paths_list.clear()
        self.plugin_paths_list.addItems(plugin_paths)
        self.cache_dir_input.setText(self.settings.get("volatility.cache_dir", ""))
        self.isf_path_input.setText(self.settings.get("volatility.isf_path", ""))
        
        # Report
        self.analyst_name_input.setText(self.settings.get("report.analyst_name", ""))
        self.company_input.setText(self.settings.get("report.company", ""))
        self.logo_path_input.setText(self.settings.get("report.logo_path", ""))
        self.template_combo.setCurrentText(self.settings.get("report.template", "default"))
        
        # Performance
        self.memory_limit_spin.setValue(self.settings.get("performance.memory_limit_mb", 4096))
        self.worker_threads_spin.setValue(self.settings.get("performance.worker_threads", 4))
        self.cache_size_spin.setValue(self.settings.get("performance.cache_size_mb", 512))
        
        # Advanced
        self.debug_mode_check.setChecked(self.settings.get("advanced.debug_mode", False))
        self.plugin_timeout_spin.setValue(self.settings.get("advanced.plugin_timeout_seconds", 300))
        plugins = self.settings.get("advanced.auto_investigation_plugins", [])
        self.auto_plugins_text.setPlainText("\n".join(plugins))
        
    def save_settings(self):
        """Save UI values to settings."""
        # Application
        self.settings.set("application.theme", self.theme_combo.currentText(), save=False)
        self.settings.set("application.auto_save", self.auto_save_check.isChecked(), save=False)
        self.settings.set("application.default_export_format", self.export_format_combo.currentText(), save=False)
        self.settings.set("application.max_concurrent_tasks", self.max_tasks_spin.value(), save=False)
        
        # VirusTotal
        self.settings.set("virustotal.api_key", self.vt_api_key_input.text(), save=False)
        self.settings.set("virustotal.cache_enabled", self.vt_cache_enabled.isChecked(), save=False)
        self.settings.set("virustotal.rate_limit", self.vt_rate_limit_spin.value(), save=False)
        
        # Volatility
        self.settings.set("volatility.symbol_path", self.symbol_path_input.text(), save=False)
        plugin_paths = [self.plugin_paths_list.item(i).text() for i in range(self.plugin_paths_list.count())]
        self.settings.set("volatility.plugin_paths", plugin_paths, save=False)
        self.settings.set("volatility.cache_dir", self.cache_dir_input.text(), save=False)
        self.settings.set("volatility.isf_path", self.isf_path_input.text(), save=False)
        
        # Report
        self.settings.set("report.analyst_name", self.analyst_name_input.text(), save=False)
        self.settings.set("report.company", self.company_input.text(), save=False)
        self.settings.set("report.logo_path", self.logo_path_input.text(), save=False)
        self.settings.set("report.template", self.template_combo.currentText(), save=False)
        
        # Performance
        self.settings.set("performance.memory_limit_mb", self.memory_limit_spin.value(), save=False)
        self.settings.set("performance.worker_threads", self.worker_threads_spin.value(), save=False)
        self.settings.set("performance.cache_size_mb", self.cache_size_spin.value(), save=False)
        
        # Advanced
        self.settings.set("advanced.debug_mode", self.debug_mode_check.isChecked(), save=False)
        self.settings.set("advanced.plugin_timeout_seconds", self.plugin_timeout_spin.value(), save=False)
        plugins_text = self.auto_plugins_text.toPlainText()
        plugins = [p.strip() for p in plugins_text.split('\n') if p.strip()]
        self.settings.set("advanced.auto_investigation_plugins", plugins, save=False)
        
        # Save all at once
        self.settings.save()
        
    def accept(self):
        """Save settings and close dialog."""
        self.save_settings()
        super().accept()
        
    def restore_defaults(self):
        """Restore all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_to_defaults()
            self.load_settings()
            
    def browse_directory(self, line_edit: QLineEdit):
        """Browse for a directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            line_edit.setText(directory)
            
    def browse_file(self, line_edit: QLineEdit, file_filter: str):
        """Browse for a file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        if file_path:
            line_edit.setText(file_path)
            
    def add_plugin_path(self):
        """Add a plugin path."""
        directory = QFileDialog.getExistingDirectory(self, "Select Plugin Directory")
        if directory:
            self.plugin_paths_list.addItem(directory)
            
    def remove_plugin_path(self):
        """Remove selected plugin path."""
        current_row = self.plugin_paths_list.currentRow()
        if current_row >= 0:
            self.plugin_paths_list.takeItem(current_row)
            
    def test_vt_api_key(self):
        """Test the VirusTotal API key."""
        api_key = self.vt_api_key_input.text()
        if not api_key:
            QMessageBox.warning(self, "No API Key", "Please enter an API key first.")
            return
            
        if self.vt_scanner:
            if self.vt_scanner.set_api_key(api_key):
                QMessageBox.information(self, "Success", "API key is valid!")
            else:
                QMessageBox.critical(self, "Error", "API key is invalid or connection failed.")
        else:
            QMessageBox.warning(self, "Error", "VirusTotal scanner not available.")
            
    def clear_vt_cache(self):
        """Clear VirusTotal cache."""
        if self.vt_scanner:
            reply = QMessageBox.question(
                self,
                "Clear Cache",
                "Are you sure you want to clear the VirusTotal cache?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.vt_scanner.clear_cache()
                QMessageBox.information(self, "Success", "Cache cleared successfully.")
        else:
            QMessageBox.warning(self, "Error", "VirusTotal scanner not available.")
