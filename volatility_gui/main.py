import sys
import os
from PyQt6.QtWidgets import QApplication
import qdarktheme

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from volatility_gui.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Apply the complete dark theme to your Qt App.
    qdarktheme.setup_theme()
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
