"""
Tokyo Night-inspired theme for Volatility3 GUI.
Color palette based on Tokyo Night color scheme.
Compact and modern UI with macOS-style rounded elements.
"""
import sys

# Tokyo Night Color Palette (Dark Theme)
class TokyoNight:
    """Tokyo Night color scheme constants (Dark)."""
    
    # Base colors
    BG_DARK = "#1a1b26"       # Main background
    BG = "#24283b"            # Secondary background
    BG_HIGHLIGHT = "#292e42"  # Highlighted background
    BG_VISUAL = "#33467c"     # Visual selection
    
    # Foreground colors
    FG = "#c0caf5"            # Main text
    FG_DARK = "#a9b1d6"       # Secondary text
    FG_GUTTER = "#3b4261"     # Gutter text
    
    # Terminal colors
    BLACK = "#15161e"
    RED = "#f7768e"
    GREEN = "#9ece6a"
    YELLOW = "#e0af68"
    BLUE = "#7aa2f7"
    MAGENTA = "#bb9af7"
    CYAN = "#7dcfff"
    WHITE = "#a9b1d6"
    
    # UI colors
    BORDER = "#414868"
    COMMENT = "#565f89"
    
    # Accent colors
    ACCENT = "#7aa2f7"        # Primary accent (blue)
    ACCENT_SECONDARY = "#bb9af7"  # Secondary accent (purple)
    SUCCESS = "#9ece6a"
    WARNING = "#e0af68"
    ERROR = "#f7768e"
    INFO = "#7dcfff"


class LightTheme:
    """Light theme color scheme constants."""
    
    # Base colors
    BG_DARK = "#ffffff"       # Main background
    BG = "#f5f5f7"            # Secondary background
    BG_HIGHLIGHT = "#e8e8ed"  # Highlighted background
    BG_VISUAL = "#d4d4d8"     # Visual selection
    
    # Foreground colors
    FG = "#1d1d1f"            # Main text
    FG_DARK = "#3d3d3f"       # Secondary text
    FG_GUTTER = "#8e8e93"     # Gutter text
    
    # Terminal colors
    BLACK = "#1d1d1f"
    RED = "#ff3b30"
    GREEN = "#34c759"
    YELLOW = "#ff9500"
    BLUE = "#007aff"
    MAGENTA = "#af52de"
    CYAN = "#5ac8fa"
    WHITE = "#f5f5f7"
    
    # UI colors
    BORDER = "#d1d1d6"
    COMMENT = "#8e8e93"
    
    # Accent colors
    ACCENT = "#007aff"        # Primary accent (blue)
    ACCENT_SECONDARY = "#af52de"  # Secondary accent (purple)
    SUCCESS = "#34c759"
    WARNING = "#ff9500"
    ERROR = "#ff3b30"
    INFO = "#5ac8fa"


def get_system_theme() -> str:
    """Detect system theme preference.
    
    Returns:
        'dark' or 'light' based on system preference.
    """
    if sys.platform == "darwin":
        # macOS
        try:
            from subprocess import run, PIPE
            result = run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True, text=True
            )
            if result.returncode == 0 and 'Dark' in result.stdout:
                return 'dark'
            return 'light'
        except Exception:
            return 'dark'
    elif sys.platform == "win32":
        # Windows
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return 'light' if value == 1 else 'dark'
        except Exception:
            return 'dark'
    else:
        # Linux - check common environment variables
        import os
        gtk_theme = os.environ.get('GTK_THEME', '').lower()
        if 'dark' in gtk_theme:
            return 'dark'
        # Check for GNOME/KDE dark mode
        try:
            from subprocess import run, PIPE
            result = run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                capture_output=True, text=True
            )
            if 'dark' in result.stdout.lower():
                return 'dark'
        except Exception:
            pass
        return 'dark'  # Default to dark


def get_stylesheet(theme: str = "dark") -> str:
    """Generate the complete application stylesheet.
    
    Args:
        theme: 'dark' or 'light'
    """
    c = TokyoNight if theme == "dark" else LightTheme
    
    return f"""
    /* ========== Global Styles ========== */
    QMainWindow, QWidget {{
        background-color: {c.BG_DARK};
        color: {c.FG};
        font-family: "Helvetica Neue", "SF Pro Text", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
        font-size: 13px;
    }}
    
    /* ========== Menu Bar (non-macOS) ========== */
    QMenuBar {{
        background-color: {c.BG};
        color: {c.FG};
        border-bottom: 1px solid {c.BORDER};
        padding: 2px 0;
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 4px 10px;
        border-radius: 6px;
        margin: 1px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {c.BG_HIGHLIGHT};
    }}
    
    QMenu {{
        background-color: {c.BG};
        border: 1px solid {c.BORDER};
        border-radius: 12px;
        padding: 8px 4px;
    }}
    
    QMenu::item {{
        padding: 6px 24px 6px 20px;
        border-radius: 8px;
        margin: 1px 4px;
    }}
    
    QMenu::item:selected {{
        background-color: {c.ACCENT};
        color: {c.BG_DARK};
    }}
    
    QMenu::separator {{
        height: 1px;
        background: {c.BORDER};
        margin: 4px 10px;
    }}
    
    /* ========== Toolbar ========== */
    QToolBar {{
        background-color: {c.BG};
        border: none;
        border-bottom: 1px solid {c.BORDER};
        spacing: 2px;
        padding: 4px 8px;
    }}
    
    QToolBar::separator {{
        width: 1px;
        background: {c.BORDER};
        margin: 4px 6px;
    }}
    
    QToolButton {{
        background-color: transparent;
        border: none;
        border-radius: 10px;
        padding: 6px 10px;
        color: {c.FG};
        font-weight: 500;
    }}
    
    QToolButton:hover {{
        background-color: {c.BG_HIGHLIGHT};
    }}
    
    QToolButton:pressed {{
        background-color: {c.BG_VISUAL};
    }}
    
    /* ========== Tab Widget - Compact & Centered ========== */
    QTabWidget::pane {{
        border: none;
        background-color: {c.BG_DARK};
        top: 0px;
    }}
    
    QTabWidget::tab-bar {{
        alignment: center;
    }}
    
    QTabBar {{
        background-color: transparent;
        qproperty-drawBase: 0;
    }}
    
    QTabBar::tab {{
        background-color: {c.BG};
        color: {c.FG_DARK};
        padding: 8px 14px;
        margin-right: 2px;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        border: none;
        min-width: 60px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {c.BG_HIGHLIGHT};
        color: {c.ACCENT};
        border-bottom: 2px solid {c.ACCENT};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {c.BG_HIGHLIGHT};
        color: {c.FG};
    }}
    
    /* ========== Buttons - Compact & Rounded ========== */
    QPushButton {{
        background-color: {c.BG_HIGHLIGHT};
        color: {c.FG};
        border: 1px solid {c.BORDER};
        border-radius: 10px;
        padding: 6px 14px;
        font-weight: 500;
        min-width: 60px;
    }}
    
    QPushButton:hover {{
        background-color: {c.ACCENT};
        color: {c.BG_DARK};
        border-color: {c.ACCENT};
    }}
    
    QPushButton:pressed {{
        background-color: {c.BG_VISUAL};
    }}
    
    QPushButton:disabled {{
        background-color: {c.BG};
        color: {c.COMMENT};
        border-color: {c.BG};
    }}
    
    /* Primary Button */
    QPushButton[primary="true"], QPushButton#primaryButton {{
        background-color: {c.ACCENT};
        color: {c.BG_DARK};
        border: none;
    }}
    
    QPushButton[primary="true"]:hover, QPushButton#primaryButton:hover {{
        background-color: {c.CYAN};
    }}
    
    /* ========== Line Edits - Compact ========== */
    QLineEdit {{
        background-color: {c.BG};
        color: {c.FG};
        border: 1px solid {c.BORDER};
        border-radius: 10px;
        padding: 6px 12px;
        selection-background-color: {c.BG_VISUAL};
    }}
    
    QLineEdit:focus {{
        border-color: {c.ACCENT};
    }}
    
    QLineEdit:disabled {{
        background-color: {c.BG_DARK};
        color: {c.COMMENT};
    }}
    
    /* ========== Text Edit - Compact ========== */
    QTextEdit, QPlainTextEdit {{
        background-color: {c.BG};
        color: {c.FG};
        border: 1px solid {c.BORDER};
        border-radius: 12px;
        padding: 8px;
        selection-background-color: {c.BG_VISUAL};
    }}
    
    QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {c.ACCENT};
    }}
    
    /* ========== Combo Box - Fixed & Compact ========== */
    QComboBox {{
        background-color: {c.BG};
        color: {c.FG};
        border: 1px solid {c.BORDER};
        border-radius: 10px;
        padding: 6px 12px;
        padding-right: 28px;
        min-width: 80px;
        min-height: 24px;
    }}
    
    QComboBox:hover {{
        border-color: {c.ACCENT};
    }}
    
    QComboBox:focus {{
        border-color: {c.ACCENT};
    }}
    
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 20px;
        border: none;
        background-color: transparent;
    }}
    
    QComboBox::down-arrow {{
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {c.FG};
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {c.BG};
        color: {c.FG};
        border: 1px solid {c.BORDER};
        border-radius: 10px;
        selection-background-color: {c.ACCENT};
        selection-color: {c.BG_DARK};
        padding: 6px;
        outline: none;
    }}
    
    QComboBox QAbstractItemView::item {{
        padding: 8px 12px;
        border-radius: 6px;
        min-height: 24px;
    }}
    
    QComboBox QAbstractItemView::item:hover {{
        background-color: {c.BG_HIGHLIGHT};
    }}
    
    QComboBox QAbstractItemView::item:selected {{
        background-color: {c.ACCENT};
        color: {c.BG_DARK};
    }}
    
    /* ========== Spin Box - Compact ========== */
    QSpinBox, QDoubleSpinBox {{
        background-color: {c.BG};
        color: {c.FG};
        border: 1px solid {c.BORDER};
        border-radius: 10px;
        padding: 6px 12px;
    }}
    
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {c.ACCENT};
    }}
    
    /* ========== Check Box ========== */
    QCheckBox {{
        color: {c.FG};
        spacing: 6px;
        background-color: transparent;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {c.BORDER};
        border-radius: 5px;
        background-color: {c.BG};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {c.ACCENT};
        border-color: {c.ACCENT};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {c.ACCENT};
    }}
    
    /* ========== Table Widget - Compact ========== */
    QTableWidget, QTableView {{
        background-color: {c.BG_DARK};
        color: {c.FG};
        border: 1px solid {c.BORDER};
        border-radius: 12px;
        gridline-color: {c.BORDER};
        selection-background-color: {c.BG_VISUAL};
        selection-color: {c.FG};
    }}
    
    QTableWidget::item, QTableView::item {{
        padding: 4px 6px;
        border-bottom: 1px solid {c.BG_HIGHLIGHT};
    }}
    
    QTableWidget::item:selected, QTableView::item:selected {{
        background-color: {c.BG_VISUAL};
    }}
    
    QTableWidget::item:hover, QTableView::item:hover {{
        background-color: {c.BG_HIGHLIGHT};
    }}
    
    QHeaderView::section {{
        background-color: {c.BG};
        color: {c.ACCENT};
        padding: 6px 6px;
        border: none;
        border-bottom: 2px solid {c.ACCENT};
        font-weight: 600;
        font-size: 11px;
    }}
    
    QHeaderView::section:hover {{
        background-color: {c.BG_HIGHLIGHT};
    }}
    
    /* ========== Scroll Bars - Compact ========== */
    QScrollBar:vertical {{
        background-color: {c.BG_DARK};
        width: 10px;
        border-radius: 5px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {c.BORDER};
        border-radius: 5px;
        min-height: 24px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {c.COMMENT};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    
    QScrollBar:horizontal {{
        background-color: {c.BG_DARK};
        height: 10px;
        border-radius: 5px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {c.BORDER};
        border-radius: 5px;
        min-width: 24px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {c.COMMENT};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    
    /* ========== Group Box - Minimal borders ========== */
    QGroupBox {{
        background-color: transparent;
        border: 1px solid {c.BORDER};
        border-radius: 14px;
        margin-top: 14px;
        padding: 12px;
        font-weight: 600;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        padding: 0 6px;
        color: {c.ACCENT};
        background-color: {c.BG_DARK};
    }}
    
    /* ========== Dock Widget ========== */
    QDockWidget {{
        background-color: {c.BG_DARK};
        color: {c.FG};
        titlebar-close-icon: none;
        titlebar-normal-icon: none;
    }}
    
    QDockWidget::title {{
        background-color: {c.BG};
        padding: 6px;
        border-bottom: 1px solid {c.BORDER};
    }}
    
    /* ========== Status Bar ========== */
    QStatusBar {{
        background-color: {c.BG};
        color: {c.FG_DARK};
        border-top: 1px solid {c.BORDER};
        padding: 2px 6px;
        font-size: 11px;
    }}
    
    QStatusBar::item {{
        border: none;
    }}
    
    /* ========== Progress Bar ========== */
    QProgressBar {{
        background-color: {c.BG};
        border: none;
        border-radius: 5px;
        height: 8px;
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {c.ACCENT}, stop:1 {c.CYAN});
        border-radius: 5px;
    }}
    
    /* ========== Dialog ========== */
    QDialog {{
        background-color: {c.BG_DARK};
        color: {c.FG};
    }}
    
    QDialogButtonBox {{
        button-layout: 0;
    }}
    
    /* ========== List Widget ========== */
    QListWidget {{
        background-color: {c.BG};
        color: {c.FG};
        border: 1px solid {c.BORDER};
        border-radius: 12px;
        padding: 6px;
    }}
    
    QListWidget::item {{
        padding: 8px;
        border-radius: 8px;
    }}
    
    QListWidget::item:selected {{
        background-color: {c.BG_VISUAL};
    }}
    
    QListWidget::item:hover {{
        background-color: {c.BG_HIGHLIGHT};
    }}
    
    /* ========== Message Box ========== */
    QMessageBox {{
        background-color: {c.BG_DARK};
    }}
    
    QMessageBox QLabel {{
        color: {c.FG};
        background-color: transparent;
    }}
    
    /* ========== Tooltip ========== */
    QToolTip {{
        background-color: {c.BG};
        color: {c.FG};
        border: 1px solid {c.BORDER};
        border-radius: 8px;
        padding: 6px 10px;
    }}
    
    /* ========== Splitter ========== */
    QSplitter::handle {{
        background-color: {c.BORDER};
    }}
    
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    
    /* ========== Labels - Transparent background ========== */
    QLabel {{
        color: {c.FG};
        background-color: transparent;
    }}
    
    QLabel[heading="true"] {{
        color: {c.ACCENT};
        font-weight: 600;
        font-size: 14px;
        background-color: transparent;
    }}
    
    /* ========== File Dialog ========== */
    QFileDialog {{
        background-color: {c.BG_DARK};
    }}
    
    /* ========== Scroll Area ========== */
    QScrollArea {{
        background-color: transparent;
        border: none;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    
    /* ========== Frame ========== */
    QFrame {{
        background-color: transparent;
    }}
    """
