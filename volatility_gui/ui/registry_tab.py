from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel, QComboBox, QLineEdit, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from volatility_gui.logic.exporter import Exporter

class RegistryTab(QWidget):
    def __init__(self):
        super().__init__()
        # Cache data for each plugin
        self.plugin_data_cache = {
            "Hive Scan": None,
            "Hive List": None,
            "Print Key": None
        }
        self.plugin_combo = None  # Will be set in init_ui
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Controls area
        controls_layout = QHBoxLayout()
        self.status_label = QLabel("Ready to analyze")
        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch()
        
        # Plugin selector
        self.plugin_combo = QComboBox()
        self.plugin_combo.addItems(["Hive Scan", "Hive List", "Print Key"])
        self.plugin_combo.currentTextChanged.connect(self.on_plugin_changed)
        controls_layout.addWidget(QLabel("Plugin:"))
        controls_layout.addWidget(self.plugin_combo)
        
        self.refresh_btn = QPushButton("Run Analysis")
        controls_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        controls_layout.addWidget(self.export_btn)
        
        layout.addLayout(controls_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter results...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Offset", "Path", "Details"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)

    # ... (existing methods)

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

    def export_results(self):
        """Export current plugin results to a file."""
        current_plugin = self.plugin_combo.currentText()
        data = self.plugin_data_cache.get(current_plugin)
        
        if not data:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Results", 
            f"{current_plugin.replace(' ', '_')}_export",
            "JSON Files (*.json);;CSV Files (*.csv);;HTML Files (*.html)"
        )
        
        if not file_path:
            return
            
        success = False
        if file_path.endswith('.json'):
            success = Exporter.export_to_json(data, file_path)
        elif file_path.endswith('.csv'):
            success = Exporter.export_to_csv(data, file_path)
        elif file_path.endswith('.html'):
            success = Exporter.export_to_html(data, file_path)
            
        if success:
            QMessageBox.information(self, "Export Success", f"Data exported to {file_path}")
        else:
            QMessageBox.critical(self, "Export Error", "Failed to export data.")

    def get_selected_plugin(self):
        """Get the currently selected plugin name."""
        plugin_map = {
            "Hive Scan": "windows.registry.hivescan.HiveScan",
            "Hive List": "windows.registry.hivelist.HiveList",
            "Print Key": "windows.registry.printkey.PrintKey"
        }
        return plugin_map.get(self.plugin_combo.currentText())
    
    def on_plugin_changed(self, plugin_name):
        """Restore cached data when plugin changes."""
        # Clear current display
        self.table.setRowCount(0)
        
        # Restore cached data if available
        cached_data = self.plugin_data_cache.get(plugin_name)
        if cached_data is not None:
            self._display_data(cached_data)
        else:
            self.status_label.setText("Ready to analyze")

    def update_table(self, data, plugin_name=None):
        """
        Update table with registry data and cache it.
        
        Args:
            data: The data to display/cache
            plugin_name: The name of the plugin this data belongs to.
                         If None, uses the currently selected plugin.
        """
        if not data:
            # Only update status if we are viewing this plugin
            if plugin_name is None or plugin_name == self.plugin_combo.currentText():
                self.status_label.setText("No registry data found")
            return
        
        # Determine which plugin this data is for
        target_plugin = plugin_name if plugin_name else self.plugin_combo.currentText()
        
        # Cache the data
        self.plugin_data_cache[target_plugin] = data
        
        # Only update display if this is the currently selected plugin
        if target_plugin == self.plugin_combo.currentText():
            self._display_data(data)
        else:
            # Just update status
            count = len(data)
            self.status_label.setText(f"Background: Loaded {count} items for {target_plugin}")
    
    def _display_data(self, data):
        """Internal method to display data without caching."""
        self.table.setRowCount(0)
        
        plugin_name = self.plugin_combo.currentText()
        
        # Update columns based on plugin
        if plugin_name == "Hive Scan":
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Offset"])
        elif plugin_name == "Hive List":
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["Offset", "FileFullPath"])
        elif plugin_name == "Print Key":
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels(["Last Write Time", "Hive Offset", "Type", "Key", "Name", "Data", "Volatile"])
        
        self.table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            if plugin_name == "Hive Scan":
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data.get('Offset', ''))))
            elif plugin_name == "Hive List":
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data.get('Offset', ''))))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(row_data.get('FileFullPath', ''))))
            elif plugin_name == "Print Key":
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data.get('Last Write Time', ''))))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(row_data.get('Hive Offset', ''))))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(row_data.get('Type', ''))))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(row_data.get('Key', ''))))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(row_data.get('Name', ''))))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(row_data.get('Data', ''))))
                self.table.setItem(row_idx, 6, QTableWidgetItem(str(row_data.get('Volatile', ''))))
            
        self.status_label.setText(f"Loaded {len(data)} registry entries")

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
