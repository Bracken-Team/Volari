from PyQt6.QtCore import QThread, pyqtSignal
import traceback

class PluginWorker(QThread):
    """Worker thread for running Volatility plugins."""
    
    started = pyqtSignal()
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        """Run the plugin function."""
        self.started.emit()
        try:
            # Add progress callback to kwargs if the function accepts it
            # This assumes the wrapper function handles 'progress_callback'
            self.kwargs['progress_callback'] = self.report_progress
            
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.error.emit(error_msg)
            
    def report_progress(self, percentage: int, message: str):
        """Callback to report progress from the plugin."""
        self.progress.emit(percentage, message)
