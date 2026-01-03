# Installation Guide

## Requirements

- **Python**: 3.9 or later
- **Operating System**: macOS, Windows 10/11, Linux (Ubuntu 20.04+)
- **RAM**: 8GB minimum, 16GB recommended for large memory dumps

## Installation Methods

### Method 1: From Source (Development)

```bash
# Clone repository
git clone https://github.com/volatilityfoundation/volatility3.git
cd volatility3

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install core + GUI dependencies
pip install -e ".[full]"
pip install -r requirements.txt
```

### Method 2: pip Install

```bash
pip install volari
```

### Method 3: Standalone Application

Download pre-built binaries from [Releases](https://github.com/volatilityfoundation/volatility3/releases):

- **macOS**: `Volari.dmg`
- **Windows**: `Volari-Setup.exe`
- **Linux**: `Volari.AppImage`

## Platform-Specific Notes

### macOS

For native window styling, install PyObjC:

```bash
pip install pyobjc-core pyobjc-framework-Cocoa
```

If the app shows "damaged" warning:

```bash
xattr -cr /Applications/Volari.app
```

### Windows

Ensure Visual C++ Redistributable is installed.

### Linux

Install Qt dependencies:

```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxkbcommon-x11-0

# Fedora
sudo dnf install xcb-util-cursor
```

## Symbol Tables

Download and extract to `volatility3/symbols/`:

- [Windows Symbols](https://downloads.volatilityfoundation.org/volatility3/symbols/windows.zip)
- [macOS Symbols](https://downloads.volatilityfoundation.org/volatility3/symbols/mac.zip)
- [Linux Symbols](https://downloads.volatilityfoundation.org/volatility3/symbols/linux.zip)

## Verify Installation

```bash
python volatility_gui/main.py
```

The GUI should launch without errors.
