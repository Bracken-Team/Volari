import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from volatility_gui.ui.main_window import MainWindow
from volatility_gui.styles import get_stylesheet, get_system_theme, TokyoNight, LightTheme
from volatility_gui.logic.settings_manager import SettingsManager


def setup_macos_window_style(window, theme: str):
    """Configure native macOS window styling for a seamless, modern look.
    
    This uses PyObjC to access Cocoa APIs and customize the window appearance:
    - Transparent titlebar that blends with content
    - Hidden title text
    - Custom background color matching the theme
    """
    try:
        import objc
        from ctypes import c_void_p
        from AppKit import (
            NSApplication, NSAppearance, NSAppearanceNameDarkAqua, NSAppearanceNameAqua,
            NSColor
        )
        
        # Get the native window handle from Qt
        win_id = window.winId().__int__()
        
        # Convert winId to NSView using objc bridge, then get its window
        ns_view = objc.objc_object(c_void_p=c_void_p(win_id))
        ns_window = ns_view.window()
        
        if ns_window is None:
            print("Warning: Could not get NSWindow from Qt window")
            return
        
        # Make titlebar transparent - this makes it blend with content
        ns_window.setTitlebarAppearsTransparent_(True)
        
        # Keep the title visible (app name "Volari" will show)
        
        # Set the appearance based on theme
        if theme == "dark":
            ns_window.setAppearance_(NSAppearance.appearanceNamed_(NSAppearanceNameDarkAqua))
            # Set window background color to match dark theme
            c = TokyoNight
        else:
            ns_window.setAppearance_(NSAppearance.appearanceNamed_(NSAppearanceNameAqua))
            c = LightTheme
        
        # Convert hex color to NSColor
        bg_color = c.BG_DARK
        r = int(bg_color[1:3], 16) / 255.0
        g = int(bg_color[3:5], 16) / 255.0
        b = int(bg_color[5:7], 16) / 255.0
        ns_window.setBackgroundColor_(NSColor.colorWithRed_green_blue_alpha_(r, g, b, 1.0))
        
        # Enable full-size content view for modern seamless look
        # NSWindowStyleMaskFullSizeContentView = 1 << 15 = 32768
        current_style = ns_window.styleMask()
        ns_window.setStyleMask_(current_style | 32768)
        
        # Make the window movable by clicking anywhere on the background
        ns_window.setMovableByWindowBackground_(True)
        
        print(f"✓ Applied macOS window styling (transparent titlebar, {theme} theme)")
        
    except ImportError as e:
        print(f"Warning: PyObjC not available for window customization: {e}")
    except Exception as e:
        print(f"Warning: Could not customize macOS window: {e}")


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
        # Use Helvetica Neue (always available on macOS) as primary
        # SF Pro may not be installed on all systems
        font.setFamilies(["Helvetica Neue", "SF Pro Text", "Helvetica", "Arial"])
    else:
        font.setFamilies(["Segoe UI", "Roboto", "Helvetica Neue", "Arial"])
    font.setPointSize(13)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    
    window = MainWindow()
    
    # macOS specific: unified title bar
    if sys.platform == "darwin":
        window.setUnifiedTitleAndToolBarOnMac(True)
    
    window.show()
    
    # Apply macOS native window styling immediately after window is shown
    if sys.platform == "darwin":
        setup_macos_window_style(window, theme)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
