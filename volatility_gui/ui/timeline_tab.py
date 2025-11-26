from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QCheckBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QSplitter, QGroupBox)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime
from typing import List
from volatility_gui.logic.timeline_aggregator import TimelineAggregator, TimelineEvent


class TimelineTab(QWidget):
    """Tab for displaying forensic timeline visualization."""
    
    def __init__(self):
        super().__init__()
        self.aggregator = TimelineAggregator()
        self.current_events: List[TimelineEvent] = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.status_label = QLabel("No timeline data loaded")
        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch()
        
        self.generate_btn = QPushButton("Generate Timeline")
        self.generate_btn.clicked.connect(self.generate_timeline)
        controls_layout.addWidget(self.generate_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_timeline)
        controls_layout.addWidget(self.clear_btn)
        
        layout.addLayout(controls_layout)
        
        # Filter checkboxes
        filter_group = QGroupBox("Event Filters")
        filter_layout = QHBoxLayout()
        
        self.process_check = QCheckBox("Process")
        self.process_check.setChecked(True)
        self.process_check.stateChanged.connect(self.update_display)
        filter_layout.addWidget(self.process_check)
        
        self.network_check = QCheckBox("Network")
        self.network_check.setChecked(True)
        self.network_check.stateChanged.connect(self.update_display)
        filter_layout.addWidget(self.network_check)
        
        self.file_check = QCheckBox("File")
        self.file_check.setChecked(True)
        self.file_check.stateChanged.connect(self.update_display)
        filter_layout.addWidget(self.file_check)
        
        self.registry_check = QCheckBox("Registry")
        self.registry_check.setChecked(True)
        self.registry_check.stateChanged.connect(self.update_display)
        filter_layout.addWidget(self.registry_check)
        
        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Splitter for timeline and table
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Timeline visualization
        self.figure = Figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        splitter.addWidget(self.canvas)
        
        # Add Navigation Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        # Connect pick event
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Event table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Type", "Description", "Details"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        splitter.addWidget(self.table)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
    def generate_timeline(self):
        """Generate timeline from available data."""
        # This will be called by MainWindow with data
        pass
        
    def load_data(self, process_data=None, network_data=None, file_data=None, registry_data=None):
        """
        Load data from various sources and generate timeline.
        
        Args:
            process_data: Process data from pslist/psscan
            network_data: Network connection data
            file_data: File scan data
            registry_data: Registry hive data
        """
        self.aggregator.clear()
        
        # Add events from each source
        if process_data:
            self.aggregator.add_process_events(process_data)
            
        if network_data:
            self.aggregator.add_network_events(network_data)
            
        if file_data:
            self.aggregator.add_file_events(file_data)
            
        if registry_data:
            self.aggregator.add_registry_events(registry_data)
            
        # Get sorted events
        self.current_events = self.aggregator.get_sorted_events()
        
        if self.current_events:
            self.status_label.setText(f"Timeline generated: {len(self.current_events)} events")
            self.update_display()
        else:
            self.status_label.setText("No timeline events found")
            
    def update_display(self):
        """Update the timeline visualization and table based on filters."""
        if not self.current_events:
            return
            
        # Filter events based on checkboxes
        filtered_events = []
        for event in self.current_events:
            if event.event_type == 'Process' and self.process_check.isChecked():
                filtered_events.append(event)
            elif event.event_type == 'Network' and self.network_check.isChecked():
                filtered_events.append(event)
            elif event.event_type == 'File' and self.file_check.isChecked():
                filtered_events.append(event)
            elif event.event_type == 'Registry' and self.registry_check.isChecked():
                filtered_events.append(event)
                
        # Update visualization
        self.plot_timeline(filtered_events)
        
        # Update table
        self.update_table(filtered_events)
        
    def on_pick(self, event):
        """Handle pick event on the timeline."""
        if event.artist != self.scatter_plot:
            return
            
        # Get index of selected point
        ind = event.ind[0]
        
        # Get corresponding event
        # We need to filter events same way as display to match indices
        filtered_events = []
        for e in self.current_events:
            if e.event_type == 'Process' and self.process_check.isChecked():
                filtered_events.append(e)
            elif e.event_type == 'Network' and self.network_check.isChecked():
                filtered_events.append(e)
            elif e.event_type == 'File' and self.file_check.isChecked():
                filtered_events.append(e)
            elif e.event_type == 'Registry' and self.registry_check.isChecked():
                filtered_events.append(e)
                
        if ind < len(filtered_events):
            # Select row in table
            self.table.selectRow(ind)
            # Scroll to row
            self.table.scrollToItem(self.table.item(ind, 0))

    def plot_timeline(self, events: List[TimelineEvent]):
        """Plot the timeline visualization."""
        self.ax.clear()
        
        if not events:
            self.ax.text(0.5, 0.5, 'No events to display', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
            
        # Prepare data for plotting
        event_types = {'Process': 0, 'Network': 1, 'File': 2, 'Registry': 3}
        colors = {'Process': '#3498db', 'Network': '#2ecc71', 'File': '#f39c12', 'Registry': '#e74c3c'}
        
        timestamps = [e.timestamp for e in events]
        y_positions = [event_types.get(e.event_type, 0) for e in events]
        event_colors = [colors.get(e.event_type, '#95a5a6') for e in events]
        
        # Plot events
        self.scatter_plot = self.ax.scatter(timestamps, y_positions, c=event_colors, s=50, alpha=0.6, edgecolors='black', linewidth=0.5, picker=5)
        
        # Formatting
        self.ax.set_yticks(list(event_types.values()))
        self.ax.set_yticklabels(list(event_types.keys()))
        self.ax.set_xlabel('Time')
        self.ax.set_title('Forensic Timeline')
        self.ax.grid(True, alpha=0.3)
        
        # Format x-axis for dates
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        self.figure.autofmt_xdate()
        
        self.canvas.draw()
        
    def update_table(self, events: List[TimelineEvent]):
        """Update the event table."""
        self.table.setRowCount(0)
        self.table.setRowCount(len(events))
        
        for row_idx, event in enumerate(events):
            # Timestamp
            timestamp_str = event.timestamp.strftime('%Y-%m-%d %H:%M:%S') if event.timestamp else 'Unknown'
            self.table.setItem(row_idx, 0, QTableWidgetItem(timestamp_str))
            
            # Type
            self.table.setItem(row_idx, 1, QTableWidgetItem(event.event_type))
            
            # Description
            self.table.setItem(row_idx, 2, QTableWidgetItem(event.description))
            
            # Details
            details_str = ', '.join([f"{k}: {v}" for k, v in event.details.items()])
            self.table.setItem(row_idx, 3, QTableWidgetItem(details_str))
            
    def clear_timeline(self):
        """Clear the timeline."""
        self.aggregator.clear()
        self.current_events = []
        self.ax.clear()
        self.canvas.draw()
        self.table.setRowCount(0)
        self.status_label.setText("Timeline cleared")
