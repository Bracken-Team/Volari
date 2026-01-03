# Developer Guide

## Project Structure

```
volatility3-GUI/
├── volatility_gui/           # Main GUI package
│   ├── __init__.py           # Package metadata
│   ├── main.py               # Entry point
│   ├── styles.py             # Theme styling
│   ├── modern_icons.py       # SVG icons
│   ├── exceptions.py         # Custom exceptions
│   ├── logic/                # Business logic
│   │   ├── config.py         # Configuration
│   │   ├── volatility_wrapper.py
│   │   ├── settings_manager.py
│   │   ├── exporter.py
│   │   └── ...
│   └── ui/                   # UI components
│       ├── main_window.py
│       ├── process_tab.py
│       └── ...
├── tests/                    # Test suite
├── docs/                     # Documentation
├── requirements.txt          # Dependencies
└── pyproject.toml            # Package config
```

## Development Setup

```bash
# Clone and setup
git clone https://github.com/volatilityfoundation/volatility3.git
cd volatility3
python3 -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -e ".[dev]"
pip install -r requirements.txt
pip install ruff pytest
```

## Code Style

We follow PEP 8 with these additions:
- Line length: 88 characters (Black default)
- Imports sorted with isort
- Type hints for public functions

### Linting

```bash
ruff check volatility_gui/
ruff check volatility_gui/ --fix  # Auto-fix
```

### Formatting

```bash
black volatility_gui/
isort volatility_gui/
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=volatility_gui
```

### Writing Tests

Tests go in `tests/` with `test_` prefix:

```python
def test_feature_name():
    assert expected == actual
```

## Adding a New Tab

1. Create `volatility_gui/ui/my_tab.py`:

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class MyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        # Add widgets
```

2. Register in `main_window.py`:

```python
from volatility_gui.ui.my_tab import MyTab

# In _init_tabs():
self.my_tab = MyTab()
self.tabs.addTab(self.my_tab, "My Tab")
```

## Building Standalone Apps

### macOS

```bash
pyinstaller volari.spec --clean --noconfirm
# Output: dist/Volari.app
```

### Windows

```bash
pyinstaller volari.spec --clean --noconfirm
# Output: dist/Volari.exe
```

### Linux AppImage

See `BUILD_LINUX.md`.

## Debugging

Enable debug logging:

```bash
VOLARI_LOG_LEVEL=DEBUG python volatility_gui/main.py
```
