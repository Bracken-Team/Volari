from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel, QComboBox, QLineEdit)
from PyQt6.QtCore import Qt

class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        # Cache data for each plugin
        self.plugin_data_cache = {
            "PS List": None,
            "PS Scan": None,
            "PS Tree": None,
            "Handles": None,
            "DLL List": None,
            "Command Line": None
        }
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
        self.plugin_combo.addItems(["PS List", "PS Scan", "PS Tree", "Handles", "DLL List", "Command Line"])
        self.plugin_combo.currentTextChanged.connect(self.on_plugin_changed)
        controls_layout.addWidget(QLabel("Plugin:"))
        controls_layout.addWidget(self.plugin_combo)
        
        self.refresh_btn = QPushButton("Start Analysis")
        self.refresh_btn.clicked.connect(lambda: self.refresh_btn.setText("Refresh"))
        # self.refresh_btn.clicked.connect(self.refresh_data) # To be connected by main window
        controls_layout.addWidget(self.refresh_btn)
        
        self.dump_btn = QPushButton("Dump Process")
        self.dump_btn.setEnabled(False)  # Disabled until a process is selected
        # self.dump_btn.clicked.connect(self.dump_process) # To be connected by main window
        controls_layout.addWidget(self.dump_btn)
        
        layout.addLayout(controls_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter results...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table view for all plugins
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.table)
        
        # Set initial columns
        self.on_plugin_changed("PS List")
    
    def on_plugin_changed(self, plugin_name):
        """Update table columns when plugin changes and restore cached data."""
        column_map = {
            "PS List": ["PID", "PPID", "ImageFileName", "Offset(V)", "Threads", "Handles", "SessionId", "Wow64", "CreateTime", "ExitTime"],
            "PS Scan": ["PID", "PPID", "ImageFileName", "Offset(V)", "Threads", "Handles", "SessionId", "Wow64", "CreateTime", "ExitTime"],
            "PS Tree": ["PID", "PPID", "ImageFileName", "Offset(V)", "Threads", "Handles", "SessionId", "Wow64", "CreateTime", "ExitTime"],
            "Handles": ["PID", "Process", "Offset", "HandleValue", "Type", "GrantedAccess", "Name"],
            "DLL List": ["PID", "Process", "Base", "Size", "Name", "Path", "LoadTime"],
            "Command Line": ["PID", "Process", "Args"]
        }
        
        columns = column_map.get(plugin_name, column_map["PS List"])
        
        # Update table columns
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Clear current display
        self.table.setRowCount(0)
        
        # Restore cached data if available
        cached_data = self.plugin_data_cache.get(plugin_name)
        if cached_data is not None:
            self._display_data(cached_data)
        else:
            self.status_label.setText("Ready to analyze")
    
    def get_selected_plugin(self):
        """Get the currently selected plugin name."""
        plugin_map = {
            "PS List": "windows.pslist.PsList",
            "PS Scan": "windows.psscan.PsScan",
            "PS Tree": "windows.pstree.PsTree",
            "Handles": "windows.handles.Handles",
            "DLL List": "windows.dlllist.DllList",
            "Command Line": "windows.cmdline.CmdLine"
        }
        return plugin_map.get(self.plugin_combo.currentText())
    
    def on_selection_changed(self):
        """Enable/disable dump button based on selection."""
        has_selection = len(self.table.selectedItems()) > 0
        self.dump_btn.setEnabled(has_selection)
    
    def get_selected_pid(self):
        """Get the PID of the currently selected process."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            pid_item = self.table.item(row, 0)
            if pid_item:
                return pid_item.text()
        return None

    def update_table(self, data):
        """
        Updates the display with process data and caches it.
        This is called when new data arrives from a plugin.
        """
        if not data:
            self.status_label.setText("No processes found")
            return
        
        # Always cache the data for the current plugin
        current_plugin = self.plugin_combo.currentText()
        self.plugin_data_cache[current_plugin] = data
        
        # Display the data
        self._display_data(data)
    
    def _display_data(self, data):
        """Internal method to display data without caching."""
        if not data:
            return
        
        # Display in table view (update_table_view will set columns)
        self.update_table_view(data)
    
    def update_table_view(self, data):
        """Update table view for most plugins."""
        plugin_name = self.plugin_combo.currentText()
        
        # Define column mappings for each plugin
        column_maps = {
            "PS List": ["PID", "PPID", "ImageFileName", "Offset(V)", "Threads", "Handles", "SessionId", "Wow64", "CreateTime", "ExitTime"],
            "PS Scan": ["PID", "PPID", "ImageFileName", "Offset(V)", "Threads", "Handles", "SessionId", "Wow64", "CreateTime", "ExitTime"],
            "PS Tree": ["PID", "PPID", "ImageFileName", "Offset(V)", "Threads", "Handles", "SessionId", "Wow64", "CreateTime", "ExitTime"],
            "Handles": ["PID", "Process", "Offset", "HandleValue", "Type", "GrantedAccess", "Name"],
            "DLL List": ["PID", "Process", "Base", "Size", "Name", "Path", "LoadTime"],
            "Command Line": ["PID", "Process", "Args"]
        }
        
        columns = column_maps.get(plugin_name, column_maps["PS List"])
        
        # Set column count and headers FIRST
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Then set row count and populate data
        self.table.setRowCount(0)
        self.table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, col_name in enumerate(columns):
                # Handle special cases for column name variations
                value = ""
                if col_name == "Offset(V)":
                    value = row_data.get("Offset(V)", row_data.get("Offset", ""))
                else:
                    value = row_data.get(col_name, "")
                
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        
        self.status_label.setText(f"Loaded {len(data)} items")

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
