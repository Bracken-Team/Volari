"""
Icon constants for Volatility3 GUI.
Uses Unicode/emoji for cross-platform compatibility.
"""


class Icons:
    """Icon constants using Unicode symbols and emoji."""
    
    # File operations
    FOLDER_OPEN = "📂"
    FILE = "📄"
    SAVE = "💾"
    
    # Navigation
    SETTINGS = "⚙️"
    MENU = "☰"
    
    # Analysis
    SEARCH = "🔍"
    SCAN = "🔬"
    INVESTIGATE = "🕵️"
    
    # Views
    LOGS = "📋"
    QUEUE = "📊"
    CHART = "📈"
    LIST = "📝"
    
    # Status
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOADING = "⏳"
    
    # Actions
    PLAY = "▶️"
    PAUSE = "⏸️"
    STOP = "⏹️"
    REFRESH = "🔄"
    EXPORT = "📤"
    IMPORT = "📥"
    
    # Categories
    PROCESS = "⚙️"
    NETWORK = "🌐"
    REGISTRY = "🗂️"
    MALWARE = "🦠"
    TIMELINE = "📅"
    IOC = "🎯"
    VIRUS = "🔬"
    
    # Report
    REPORT = "📄"
    PDF = "📑"
    
    # System
    INFO_CIRCLE = "ℹ️"
    MEMORY = "💾"
    OS = "💻"


def get_icon_text(icon: str, text: str) -> str:
    """Combine an icon with text for display."""
    return f"{icon}  {text}"
