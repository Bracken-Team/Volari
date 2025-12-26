import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from volatility_gui.ui.main_window import MainWindow
from volatility_gui.styles import get_stylesheet, get_system_theme
from volatility_gui.logic.settings_manager import SettingsManager

def main():
    # Load settings first to get theme preference
    settings = SettingsManager()
    theme_setting = settings.get("application.theme", "dark")
    
    # Determine actual theme to use
    if theme_setting == "system":
        theme = get_system_theme()
    else:
        theme = theme_setting
    
    # Enable macOS dark mode for the app BEFORE creating QApplication
    if sys.platform == "darwin":
        os.environ['QT_MAC_WANTS_LAYER'] = '1'
        # Force dark mode appearance if theme is dark
        if theme == "dark":
            try:
                from Foundation import NSBundle
                from AppKit import NSApplication, NSAppearance, NSAppearanceNameDarkAqua
                # Set the app bundle info to prefer dark mode
                bundle = NSBundle.mainBundle()
                info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                if info:
                    info['NSRequiresAquaSystemAppearance'] = False
            except ImportError:
                pass  # PyObjC not available
    
    app = QApplication(sys.argv)
    
    # Force dark appearance on macOS after app is created
    if sys.platform == "darwin" and theme == "dark":
        try:
            from AppKit import NSApplication, NSAppearance, NSAppearanceNameDarkAqua
            NSApplication.sharedApplication().setAppearance_(
                NSAppearance.appearanceNamed_(NSAppearanceNameDarkAqua)
            )
        except ImportError:
            pass  # PyObjC not available
    
    # Apply custom theme
    app.setStyleSheet(get_stylesheet(theme))
    
    # Set global font for better readability
    font = QFont()
    if sys.platform == "darwin":  # macOS
        font.setFamily("SF Pro Display")  # Use San Francisco font
    else:
        font.setFamily("Segoe UI")
    font.setPointSize(13)
    app.setFont(font)
    
    window = MainWindow()
    
    # macOS specific: unified title bar
    if sys.platform == "darwin":
        window.setUnifiedTitleAndToolBarOnMac(True)
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
