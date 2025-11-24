from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel, QComboBox)
from PyQt6.QtCore import Qt

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
        
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Offset", "Path", "Details"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)

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

    def update_table(self, data):
        """Update table with registry data and cache it."""
        if not data:
            self.status_label.setText("No registry data found")
            return
        
        # Always cache the data for current plugin
        current_plugin = self.plugin_combo.currentText()
        self.plugin_data_cache[current_plugin] = data
        
        # Display the data
        self._display_data(data)
    
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
