"""
Volari - Main entry point for the GUI application.

This module initializes the Qt application, applies theming,
and launches the main window.
"""

import sys
import os
import logging
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon

if TYPE_CHECKING:
    from volatility_gui.ui.main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from volatility_gui.ui.main_window import MainWindow
from volatility_gui.styles import get_stylesheet, get_system_theme, TokyoNight, LightTheme
from volatility_gui.logic.settings_manager import SettingsManager


def setup_macos_window_style(window: "MainWindow", theme: str) -> None:
    """Configure native macOS window styling for a seamless, modern look.

    Uses PyObjC to access Cocoa APIs and customize the window appearance:
    - Transparent titlebar that blends with content
    - Custom background color matching the theme

    Args:
        window: The main application window.
        theme: The current theme name ('dark' or 'light').
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
            logger.warning("Could not get NSWindow from Qt window")
            return

        # Make titlebar transparent - this makes it blend with content
        ns_window.setTitlebarAppearsTransparent_(True)

        # Set the appearance based on theme
        if theme == "dark":
            ns_window.setAppearance_(NSAppearance.appearanceNamed_(NSAppearanceNameDarkAqua))
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

        logger.info("Applied macOS window styling (transparent titlebar, %s theme)", theme)

    except ImportError as e:
        logger.debug("PyObjC not available for window customization: %s", e)
    except Exception as e:
        logger.warning("Could not customize macOS window: %s", e)


def _setup_macos_app_identity(theme: str) -> None:
    """Set up macOS-specific application identity (dock name, icon)."""
    os.environ['QT_MAC_WANTS_LAYER'] = '1'

    try:
        from Foundation import NSBundle
        from AppKit import NSAppearance, NSAppearanceNameDarkAqua

        # Set the app name in the dock and menu bar
        bundle = NSBundle.mainBundle()
        info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
        if info:
            info['CFBundleName'] = 'Volari'
            info['CFBundleDisplayName'] = 'Volari'
            if theme == "dark":
                info['NSRequiresAquaSystemAppearance'] = False
    except ImportError:
        logger.debug("PyObjC not available for macOS identity setup")


def _apply_macos_dark_mode() -> None:
    """Force dark appearance on macOS."""
    try:
        from AppKit import NSApplication, NSAppearance, NSAppearanceNameDarkAqua
        NSApplication.sharedApplication().setAppearance_(
            NSAppearance.appearanceNamed_(NSAppearanceNameDarkAqua)
        )
    except ImportError:
        pass


def _set_dock_icon(icon_path: str) -> None:
    """Set the macOS dock icon."""
    try:
        from AppKit import NSApplication, NSImage
        ns_app = NSApplication.sharedApplication()
        ns_image = NSImage.alloc().initWithContentsOfFile_(icon_path)
        if ns_image:
            ns_app.setApplicationIconImage_(ns_image)
    except ImportError:
        pass


def main() -> None:
    """Main entry point for Volari."""
    # Load settings first to get theme preference
    settings = SettingsManager()
    theme_setting = settings.get("application.theme", "dark")

    # Determine actual theme to use
    if theme_setting == "system":
        theme = get_system_theme()
    else:
        theme = theme_setting

    # macOS-specific setup before creating QApplication
    if sys.platform == "darwin":
        _setup_macos_app_identity(theme)

    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Volari")
    app.setApplicationDisplayName("Volari")
    app.setOrganizationName("Volatility")
    app.setOrganizationDomain("volatility.org")

    # Force dark appearance on macOS after app is created
    if sys.platform == "darwin" and theme == "dark":
        _apply_macos_dark_mode()

    # Apply custom theme stylesheet
    app.setStyleSheet(get_stylesheet(theme))

    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "volari_icon.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

        if sys.platform == "darwin":
            _set_dock_icon(icon_path)

    # Set global font for better readability
    font = QFont()
    if sys.platform == "darwin":
        # Use only fonts that are always available on macOS to avoid 93ms font scan
        font.setFamilies(["Helvetica Neue", "Helvetica", "Arial"])
    else:
        font.setFamilies(["Segoe UI", "Roboto", "Helvetica Neue", "Arial"])
    font.setPointSize(13)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    # Create and show main window
    window = MainWindow()

    if sys.platform == "darwin":
        window.setUnifiedTitleAndToolBarOnMac(True)

    window.show()

    # Apply macOS native window styling after window is shown
    if sys.platform == "darwin":
        setup_macos_window_style(window, theme)

    logger.info("Volari started successfully")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
