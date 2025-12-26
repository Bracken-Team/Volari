import logging
from PyQt6.QtWidgets import QDockWidget, QTextEdit, QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, QObject, Qt

class LogSignal(QObject):
    """Signal for thread-safe logging."""
    log_record = pyqtSignal(str)

class QtLogHandler(logging.Handler):
    """Custom logging handler that emits a signal for each log record."""
    
    def __init__(self):
        super().__init__()
        self.signal = LogSignal()
        
    def emit(self, record):
        msg = self.format(record)
        self.signal.log_record.emit(msg)

class LogViewer(QDockWidget):
    """Dock widget for displaying logs."""
    
    def __init__(self, parent=None):
        super().__init__("Logs", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea
        )
        
        # Enable close, float, and move features
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        
        # Tokyo Night theme styling
        self.setStyleSheet("""
            QDockWidget {
                background-color: #1a1b26;
                color: #c0caf5;
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
        
        # Main widget
        widget = QWidget()
        widget.setStyleSheet("background-color: #1a1b26;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Text area with dark theme
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                font-family: 'SF Mono', 'Menlo', 'Consolas', monospace;
                font-size: 11px;
                background-color: #1a1b26;
                color: #a9b1d6;
                border: 1px solid #414868;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.text_edit)
        
        self.setWidget(widget)
        
        # Setup logging
        self.handler = QtLogHandler()
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.handler.signal.log_record.connect(self.append_log)
        
        # Add handler to root logger
        logging.getLogger().addHandler(self.handler)
        logging.getLogger().setLevel(logging.INFO)
        
    def append_log(self, msg):
        """Append log message to the text area."""
        self.text_edit.append(msg)
        # Auto-scroll
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)
        
    def closeEvent(self, event):
        """Remove handler when widget is closed (or hidden)."""
        # We might want to keep capturing logs even if hidden, so maybe don't remove handler here.
        # But if the widget is destroyed, we should remove it.
        # For now, let's keep it simple.
        super().closeEvent(event)
