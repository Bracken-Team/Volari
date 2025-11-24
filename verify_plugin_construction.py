import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

# Mock qdarktheme and PyQt6 to avoid GUI dependencies
sys.modules["qdarktheme"] = MagicMock()
sys.modules["PyQt6"] = MagicMock()
sys.modules["PyQt6.QtWidgets"] = MagicMock()
sys.modules["PyQt6.QtGui"] = MagicMock()
sys.modules["PyQt6.QtCore"] = MagicMock()

from volatility_gui.logic.volatility_wrapper import VolatilityWrapper

def test_plugin_construction():
    # Initialize wrapper
    vw = VolatilityWrapper()
    
    # Check if construct_plugin is available via the imported module
    # We can't easily mock the internal volatility calls without complex setup,
    # but we can check if the code path that uses construct_plugin is at least reachable/importable
    # and doesn't crash on import or init.
    
    print("Initialization Success")
    
    # To truly test run_plugin, we'd need a valid memory dump or extensive mocking.
    # For now, we verified that the module imports and initializes, which confirms the syntax and import fix.
    
if __name__ == "__main__":
    test_plugin_construction()
