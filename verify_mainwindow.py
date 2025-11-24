import sys
import os
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication

# Mock qdarktheme to avoid import error during test if not needed
sys.modules["qdarktheme"] = MagicMock()

# Add project root to path
sys.path.append(os.getcwd())

from volatility_gui.ui.main_window import MainWindow
from PyQt6.QtWidgets import QMessageBox

# Mock QMessageBox
QMessageBox.warning = MagicMock()
QMessageBox.critical = MagicMock()

def test_run_plugin():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Mock the vol_wrapper
    window.vol_wrapper = MagicMock()
    window.vol_wrapper.run_plugin.return_value = [{"PID": 123, "Name": "test.exe"}]
    
    # Mock the callback
    callback = MagicMock()
    
    # Test case 1: No file loaded
    window.run_plugin("test.plugin", callback)
    # Should show warning (mocked QMessageBox) but we can check if run_plugin was NOT called
    window.vol_wrapper.run_plugin.assert_not_called()
    
    # Test case 2: File loaded
    window.current_dump_path = "/path/to/dump.mem"
    window.run_plugin("test.plugin", callback)
    
    window.vol_wrapper.run_plugin.assert_called_with("test.plugin", "/path/to/dump.mem")
    callback.assert_called_with([{"PID": 123, "Name": "test.exe"}])
    
    print("Verification Success")

if __name__ == "__main__":
    test_run_plugin()
