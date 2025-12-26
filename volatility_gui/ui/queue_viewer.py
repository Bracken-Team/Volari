from PyQt6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QLabel, QProgressBar, QScrollArea, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from volatility_gui.logic.investigation_queue import InvestigationQueue, TaskStatus


class TaskCard(QFrame):
    """A card widget representing a single task."""
    
    def __init__(self, task, queue, parent_window, queue_viewer, parent=None):
        super().__init__(parent)
        self.task = task
        self.queue = queue
        self.parent_window = parent_window
        self.queue_viewer = queue_viewer
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Top row: Task name and status
        top_layout = QHBoxLayout()
        
        # Task name (larger font, light text for dark theme)
        self.name_label = QLabel(self.task.name)
        self.name_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #c0caf5;
            background-color: transparent;
            padding: 2px;
        """)
        top_layout.addWidget(self.name_label)
        
        top_layout.addStretch()
        
        # Status badge
        self.status_label = QLabel()
        self.status_label.setStyleSheet("padding: 4px 8px; border-radius: 6px; font-size: 11px;")
        self.update_status_badge()
        top_layout.addWidget(self.status_label)
        
        layout.addLayout(top_layout)
        
        # Progress bar with dark theme
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        # Clamp progress to valid range
        clamped_progress = max(0, min(100, self.task.progress))
        self.progress_bar.setValue(clamped_progress)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(24)
        # Dark theme progress bar
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #414868;
                border-radius: 6px;
                text-align: center;
                background-color: #1a1b26;
                color: #c0caf5;
            }
            QProgressBar::chunk {
                background-color: #9ece6a;
                border-radius: 5px;
            }
        """)
        self.update_progress_format()
        layout.addWidget(self.progress_bar)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(5)
        
        # Pause/Resume button
        if self.task.status == TaskStatus.RUNNING:
            self.pause_btn = QPushButton("⏸ Pause")
            self.pause_btn.clicked.connect(self.pause_task)
            actions_layout.addWidget(self.pause_btn)
        elif self.task.status == TaskStatus.PAUSED:
            self.resume_btn = QPushButton("▶ Resume")
            self.resume_btn.clicked.connect(self.resume_task)
            actions_layout.addWidget(self.resume_btn)
        
        # Retry button (only for failed tasks)
        if self.task.status == TaskStatus.FAILED:
            self.retry_btn = QPushButton("🔄 Retry")
            self.retry_btn.clicked.connect(self.retry_task)
            self.retry_btn.setStyleSheet("color: #1976D2; font-weight: bold;")
            actions_layout.addWidget(self.retry_btn)
        
        # Prioritize button (only for pending)
        if self.task.status == TaskStatus.PENDING:
            self.priority_btn = QPushButton("⬆ Move to Front")
            self.priority_btn.clicked.connect(self.prioritize_task)
            actions_layout.addWidget(self.priority_btn)
        
        # Remove button (not for running)
        if self.task.status != TaskStatus.RUNNING:
            self.remove_btn = QPushButton("✕ Remove")
            self.remove_btn.clicked.connect(self.remove_task)
            self.remove_btn.setStyleSheet("color: #d32f2f;")
            actions_layout.addWidget(self.remove_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Update card background based on status
        self.update_background()
        
    def update_status_badge(self):
        """Update the status badge appearance."""
        status_styles = {
            TaskStatus.PENDING: ("⏳ Pending", "#FFF9C4", "#F57F17"),
            TaskStatus.RUNNING: ("▶ Running", "#BBDEFB", "#1976D2"),
            TaskStatus.PAUSED: ("⏸ Paused", "#FFE0B2", "#E65100"),
            TaskStatus.COMPLETED: ("✓ Complete", "#C8E6C9", "#388E3C"),
            TaskStatus.FAILED: ("✗ Failed", "#FFCDD2", "#D32F2F"),
        }
        
        text, bg_color, text_color = status_styles.get(self.task.status, ("Unknown", "#E0E0E0", "#000000"))
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"padding: 4px 8px; border-radius: 3px; font-size: 11px; "
            f"background-color: {bg_color}; color: {text_color}; font-weight: bold;"
        )
        
    def update_background(self):
        """Update card background based on status."""
        # Dark theme status colors
        bg_colors = {
            TaskStatus.PENDING: "#2a2d3d",
            TaskStatus.RUNNING: "#1a2a4a",
            TaskStatus.PAUSED: "#3a2a1a",
            TaskStatus.COMPLETED: "#1a3a2a",
            TaskStatus.FAILED: "#3a1a1a",
        }
        
        bg_color = bg_colors.get(self.task.status, "#24283b")
        self.setStyleSheet(f"TaskCard {{ background-color: {bg_color}; border-radius: 8px; border: 1px solid #414868; }}")
        
    def update_progress_format(self):
        """Update progress bar format text."""
        if self.task.status == TaskStatus.FAILED and self.task.error:
            self.progress_bar.setFormat(f"Error: {self.task.error[:30]}...")
        elif self.task.status == TaskStatus.PAUSED:
            self.progress_bar.setFormat("⏸ Paused")
        elif self.task.status == TaskStatus.PENDING:
            self.progress_bar.setFormat("⏳ Waiting...")
        elif self.task.status == TaskStatus.RUNNING:
            self.progress_bar.setFormat(f"{self.task.progress}%")
        elif self.task.status == TaskStatus.COMPLETED:
            self.progress_bar.setFormat("✓ Complete")
            
    def pause_task(self):
        """Pause this task."""
        self.queue.pause_task(self.task.task_id)
        if self.parent_window and hasattr(self.parent_window, 'pause_worker'):
            self.parent_window.pause_worker(self.task.task_id)
        # Continue processing the queue after pausing (unless Pause All is active)
        if not self.queue_viewer.is_paused:
            if self.parent_window and hasattr(self.parent_window, 'process_next_task'):
                self.parent_window.process_next_task()
            
    def resume_task(self):
        """Resume this task."""
        self.queue.resume_task(self.task.task_id)
        if self.parent_window and hasattr(self.parent_window, 'process_next_task'):
            self.parent_window.process_next_task()
            
    def prioritize_task(self):
        """Move this task to front."""
        # Allow prioritizing as long as we're not trying to move it ahead of a running task
        # The queue will handle the ordering correctly
        self.queue.prioritize_task(self.task.task_id)
        
    def retry_task(self):
        """Retry a failed task."""
        self.queue.retry_task(self.task.task_id)
        # Trigger queue processing to start the retried task
        if self.parent_window and hasattr(self.parent_window, 'process_next_task'):
            self.parent_window.process_next_task()
        
    def remove_task(self):
        """Remove this task."""
        self.queue.remove_task(self.task.task_id)


class QueueViewer(QDockWidget):
    """Widget to display the investigation queue with card-based layout."""
    
    def __init__(self, queue: InvestigationQueue, parent=None):
        super().__init__("Investigation Queue", parent)
        self.queue = queue
        self.parent_window = parent
        self.is_paused = False
        self.task_cards = {}  # Map task_id to TaskCard widget
        
        # Enable close, float, and move features
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        
        # Tokyo Night theme colors
        self.setStyleSheet("""
            QDockWidget {
                background-color: #1a1b26;
                color: #c0caf5;
                titlebar-close-icon: url(none);
            }
            QDockWidget::title {
                background-color: #24283b;
                color: #c0caf5;
                padding: 8px;
                font-weight: bold;
            }
            QDockWidget::close-button, QDockWidget::float-button {
                background: #414868;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QDockWidget::close-button:hover, QDockWidget::float-button:hover {
                background: #7aa2f7;
            }
        """)
        
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """Initialize the UI."""
        # Main widget
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: #1a1b26;")
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        summary_frame.setStyleSheet("background-color: #24283b; border-radius: 8px; padding: 8px; border: 1px solid #414868;")
        summary_layout = QHBoxLayout(summary_frame)
        
        self.total_label = QLabel("Total: 0")
        self.pending_label = QLabel("⏳ 0")
        self.running_label = QLabel("▶ 0")
        self.paused_label = QLabel("⏸ 0")
        self.completed_label = QLabel("✓ 0")
        self.failed_label = QLabel("✗ 0")
        
        for label in [self.total_label, self.pending_label, self.running_label, 
                      self.paused_label, self.completed_label, self.failed_label]:
            label.setStyleSheet("font-weight: bold; padding: 2px 5px; color: #c0caf5; background: transparent;")
        
        separator = QLabel("|")
        separator.setStyleSheet("color: #414868; background: transparent;")
        
        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(separator)
        summary_layout.addWidget(self.pending_label)
        summary_layout.addWidget(self.running_label)
        summary_layout.addWidget(self.paused_label)
        summary_layout.addWidget(self.completed_label)
        summary_layout.addWidget(self.failed_label)
        summary_layout.addStretch()
        
        layout.addWidget(summary_frame)
        
        # Scroll area for task cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_layout.addStretch()
        
        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.pause_all_btn = QPushButton("⏸ Pause All")
        self.pause_all_btn.clicked.connect(self.toggle_pause_all)
        button_layout.addWidget(self.pause_all_btn)
        
        self.clear_btn = QPushButton("Clear Completed")
        self.clear_btn.clicked.connect(self.clear_completed)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.setWidget(main_widget)
        
    def connect_signals(self):
        """Connect queue signals to update methods."""
        self.queue.task_added.connect(lambda tid: self.refresh_cards())
        self.queue.task_started.connect(lambda tid: self.refresh_cards())
        self.queue.task_completed.connect(lambda tid, res: self.refresh_cards())
        self.queue.task_failed.connect(lambda tid, err: self.refresh_cards())
        self.queue.task_progress.connect(self.update_task_progress)
        
    def refresh_cards(self):
        """Refresh all task cards."""
        # Remove old cards
        for card in self.task_cards.values():
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        self.task_cards.clear()
        
        # Create new cards
        tasks = self.queue.get_all_tasks()
        for task in tasks:
            card = TaskCard(task, self.queue, self.parent_window, self)
            self.task_cards[task.task_id] = card
            # Insert before the stretch
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        
        # Update summary
        self.update_summary()
        
    def update_task_progress(self, task_id: str, percentage: int, message: str):
        """Update progress for a specific task."""
        if task_id in self.task_cards:
            card = self.task_cards[task_id]
            if percentage == -1:
                card.progress_bar.setFormat(message if message else "Processing...")
            else:
                # Clamp percentage to valid range
                clamped = max(0, min(100, percentage))
                card.progress_bar.setValue(clamped)
                card.progress_bar.setFormat(f"{clamped}%")
                
    def update_summary(self):
        """Update the summary labels."""
        summary = self.queue.get_summary()
        self.total_label.setText(f"Total: {summary['total']}")
        self.pending_label.setText(f"⏳ {summary['pending']}")
        self.running_label.setText(f"▶ {summary['running']}")
        self.paused_label.setText(f"⏸ {summary.get('paused', 0)}")
        self.completed_label.setText(f"✓ {summary['completed']}")
        self.failed_label.setText(f"✗ {summary['failed']}")
        
    def toggle_pause_all(self):
        """Toggle pause for all tasks."""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_all_btn.setText("▶ Resume All")
            # Pause all running tasks
            for task in self.queue.get_all_tasks():
                if task.status == TaskStatus.RUNNING:
                    self.queue.pause_task(task.task_id)
                    if self.parent_window and hasattr(self.parent_window, 'pause_worker'):
                        self.parent_window.pause_worker(task.task_id)
            # Do NOT continue processing - we want everything paused
        else:
            self.pause_all_btn.setText("⏸ Pause All")
            # Resume all paused tasks
            for task in self.queue.get_all_tasks():
                if task.status == TaskStatus.PAUSED:
                    self.queue.resume_task(task.task_id)
            if self.parent_window and hasattr(self.parent_window, 'process_next_task'):
                self.parent_window.process_next_task()
        
        self.refresh_cards()
        
    def clear_completed(self):
        """Clear completed and failed tasks from the queue."""
        tasks_to_remove = []
        for task_id, task in self.queue.tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                tasks_to_remove.append(task_id)
                
        for task_id in tasks_to_remove:
            self.queue.remove_task(task_id)
                
        self.refresh_cards()
