from PyQt6.QtCore import QThread, pyqtSignal
import gc

class GarbageCollectionWorker(QThread):
    finished = pyqtSignal()

    def run(self):
        gc.collect()
        self.finished.emit()
