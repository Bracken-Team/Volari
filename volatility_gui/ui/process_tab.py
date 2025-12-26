from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel, QComboBox, QLineEdit, QMessageBox, QFileDialog,
                             QMenu, QApplication, QAbstractItemView)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from volatility_gui.logic.exporter import Exporter
from volatility_gui.ui.tab_utils import setup_table_copy_on_double_click

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
        self.column_widths = {}
        self.current_plugin = None
        self.init_ui()
    
    def showEvent(self, event):
        """Called when the tab becomes visible. Ensures cached data is displayed."""
        super().showEvent(event)
        # Ensure current plugin's data is displayed when tab becomes visible
        current_plugin = self.plugin_combo.currentText()
        cached_data = self.plugin_data_cache.get(current_plugin)
        if cached_data is not None and self.table.rowCount() == 0:
            self._display_data(cached_data)

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
        
        self.refresh_btn = QPushButton("Run Analysis")
        # Button text will be updated to "Refresh" when data is loaded
        controls_layout.addWidget(self.refresh_btn)
        
        self.dump_btn = QPushButton("Dump Process")
        self.dump_btn.setEnabled(False)  # Disabled until a process is selected
        # self.dump_btn.clicked.connect(self.dump_process) # To be connected by main window
        controls_layout.addWidget(self.dump_btn)

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
        
        # Table view for all plugins
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Make table non-editable with copy-on-double-click
        setup_table_copy_on_double_click(self.table)
        
        layout.addWidget(self.table)

    def show_context_menu(self, position):
        """Show context menu for table."""
        menu = QMenu()
        
        scan_action = QAction("Scan with VirusTotal", self)
        scan_action.triggered.connect(self.scan_selected_process_vt)
        menu.addAction(scan_action)
        
        dump_action = QAction("Dump Process", self)
        dump_action.triggered.connect(self.dump_process)
        menu.addAction(dump_action)
        
        menu.exec(self.table.viewport().mapToGlobal(position))

    def scan_selected_process_vt(self):
        """Scan selected process with VirusTotal."""
        pid = self.get_selected_pid()
        if not pid:
            QMessageBox.warning(self, "Error", "Please select a process to scan.")
            return
            
        # Get main window and wrapper
        main_window = self.window()
        if not hasattr(main_window, 'vol_wrapper') or not hasattr(main_window, 'current_dump_path'):
            QMessageBox.warning(self, "Error", "Volatility wrapper not found")
            return
            
        if not main_window.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return
            
        # Check if VT API key is configured
        if not hasattr(main_window, 'virustotal_tab') or not main_window.virustotal_tab.scanner.api_key:
            reply = QMessageBox.question(
                self,
                "API Key Required",
                "VirusTotal API key is not configured. Would you like to configure it now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                main_window.tabs.setCurrentWidget(main_window.virustotal_tab)
                main_window.virustotal_tab.open_settings()
            return

        # Show progress
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog(f"Dumping and hashing process {pid}...\nThis may take a moment.", "Cancel", 0, 0, self)
        progress.setWindowTitle("Scanning Process")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(False)
        progress.show()
        
        # Run in worker thread to avoid freezing
        def run_scan(*args, **kwargs):
            try:
                # 1. Calculate hash
                file_hash = main_window.vol_wrapper.calculate_process_hash(
                    main_window.current_dump_path, 
                    pid
                )
                return file_hash
            except Exception as e:
                print(f"Error in run_scan: {e}")
                return None
            
        def on_scan_complete(file_hash):
            progress.close()
            if not file_hash:
                QMessageBox.critical(self, "Error", "Failed to calculate process hash.\nCheck logs for details.")
                return
                
            # 2. Scan hash with VT
            # Switch to VT tab and add hash
            main_window.tabs.setCurrentWidget(main_window.virustotal_tab)
            main_window.virustotal_tab.add_hashes_to_table([file_hash], f"Process {pid}")
            main_window.virustotal_tab.start_scan()
            
        # Execute
        if hasattr(main_window, 'run_worker'):
            main_window.run_worker(run_scan, on_scan_complete)
            
            # Connect cancel button
            progress.canceled.connect(lambda: None) # We can't easily cancel the thread, but we can close the dialog
        else:
            # Fallback if run_worker not available
            file_hash = run_scan()
            on_scan_complete(file_hash)
            
    def dump_process(self):
        """Dump the selected process."""
        pid = self.get_selected_pid()
        if not pid:
            QMessageBox.warning(self, "Error", "Please select a process to dump.")
            return
            
        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return
            
        # Get main window and wrapper
        main_window = self.window()
        if not hasattr(main_window, 'vol_wrapper') or not hasattr(main_window, 'current_dump_path'):
            QMessageBox.warning(self, "Error", "Volatility wrapper not found")
            return
            
        if not main_window.current_dump_path:
            QMessageBox.warning(self, "Error", "Please load a memory dump first.")
            return
            
        # Use main_window.run_worker to prevent freezing
        if hasattr(main_window, 'run_worker'):
            main_window.run_worker(
                main_window.vol_wrapper.dump_process,
                lambda res: QMessageBox.information(self, "Success", f"Process dumped to:\n{res}"),
                main_window.current_dump_path, pid, output_dir
            )
        else:
            QMessageBox.warning(self, "Error", "Worker functionality not available")
        
        # Set initial columns
        self.on_plugin_changed("PS List")

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
            
        success, message = False, "Unsupported format"
        if file_path.endswith('.json'):
            success, message = Exporter.export_to_json(data, file_path)
        elif file_path.endswith('.csv'):
            success, message = Exporter.export_to_csv(data, file_path)
        elif file_path.endswith('.html'):
            success, message = Exporter.export_to_html(data, file_path)
            
        if success:
            QMessageBox.information(self, "Export Success", message)
        else:
            QMessageBox.critical(self, "Export Error", message)
    
    def on_plugin_changed(self, plugin_name):
        """Update table columns when plugin changes and restore cached data."""
        # Save current column widths before switching
        if self.current_plugin and self.current_plugin in self.plugin_data_cache:
            self.column_widths[self.current_plugin] = self.table.horizontalHeader().saveState()
            
        self.current_plugin = plugin_name
        
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
            
        # Restore column widths if available
        if plugin_name in self.column_widths:
            self.table.horizontalHeader().restoreState(self.column_widths[plugin_name])
        else:
            # Reset to default if no saved state
            # We use a default width of 120 and let the last section stretch
            for i in range(self.table.columnCount()):
                self.table.setColumnWidth(i, 120)
    
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

    def update_table(self, data, plugin_name=None):
        """
        Updates the display with process data and caches it.
        This is called when new data arrives from a plugin.
        
        Args:
            data: The data to display/cache
            plugin_name: The name of the plugin this data belongs to. 
                         If None, uses the currently selected plugin.
        """
        if not data:
            # Only update status if we are viewing this plugin
            if plugin_name is None or plugin_name == self.plugin_combo.currentText():
                self.status_label.setText("No data found")
            return
        
        # Determine which plugin this data is for
        target_plugin = plugin_name if plugin_name else self.plugin_combo.currentText()
        
        # Cache the data
        self.plugin_data_cache[target_plugin] = data
        
        # Update button text to "Refresh" since we have data now
        self.refresh_btn.setText("Refresh")
        
        # Only update display if this is the currently selected plugin
        if target_plugin == self.plugin_combo.currentText():
            self._display_data(data)
        else:
            # Just update status to let user know data arrived
            count = len(data)
            self.status_label.setText(f"Background: Loaded {count} items for {target_plugin}")
    
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
        
        # Performance optimization: Disable sorting and updates during bulk population
        self.table.setSortingEnabled(False)
        self.table.setUpdatesEnabled(False)
        
        try:
            # Then set row count and populate data
            self.table.setRowCount(0)
            self.table.setRowCount(len(data))
            
            for row_idx, row_data in enumerate(data):
                for col_idx, col_name in enumerate(columns):
                    # Ensure we handle different data structures (dict or object)
                    val = row_data.get(col_name, "") if isinstance(row_data, dict) else getattr(row_data, col_name, "")
                    
                    item = QTableWidgetItem(str(val))
                    # Add tooltip for long content
                    item.setToolTip(str(val))
                    
                    self.table.setItem(row_idx, col_idx, item)
        finally:
            self.table.setUpdatesEnabled(True)
            self.table.setSortingEnabled(True)
        
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
