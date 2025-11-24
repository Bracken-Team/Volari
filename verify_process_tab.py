import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

# Mock qdarktheme and PyQt6
sys.modules["qdarktheme"] = MagicMock()
from PyQt6.QtWidgets import QApplication, QTableWidget

from volatility_gui.ui.process_tab import ProcessTab

def test_process_tab_update():
    app = QApplication(sys.argv)
    tab = ProcessTab()
    
    # Test data with Offset(V)
    data_v = [
        {"PID": 123, "PPID": 1, "ImageFileName": "test.exe", "Offset(V)": "0x1234", "Threads": 5, "Handles": 10}
    ]
    
    tab.update_table(data_v)
    
    # Check if row was added
    if tab.table.rowCount() != 1:
        print("Error: Row count mismatch")
        return
        
    # Check Offset column (index 3)
    offset_item = tab.table.item(0, 3)
    if offset_item.text() != "0x1234":
        print(f"Error: Offset mismatch. Expected 0x1234, got {offset_item.text()}")
        return

    print("Verification Success")

if __name__ == "__main__":
    test_process_tab_update()
