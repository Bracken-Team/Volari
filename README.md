# Volari - Memory Forensics GUI

<p align="center">
  <img src="volatility_gui/resources/volari_icon.png" alt="Volari Logo" width="256"/>
</p>

**Volari** is a modern, cross-platform graphical user interface for [Volatility 3](https://github.com/volatilityfoundation/volatility3), the world's most widely used memory forensics framework.

![Volari Screenshot](docs/screenshots/main_window.png)
*Screenshot placeholder - add main window screenshot*

---

## ✨ Features

- **🎨 Modern Dark Theme** - Tokyo Night-inspired design with seamless macOS integration
- **📊 Interactive Dashboard** - OS info, processes, network, registry, files, and more
- **🔍 Auto-Investigation** - Queue and run multiple plugins automatically
- **📈 Timeline Analysis** - Visualize events with interactive charts
- **🦠 Malware Detection** - IOC scanning and VirusTotal integration
- **📄 PDF Reports** - Generate professional forensic reports
- **⚡ Queue System** - Pause, resume, and prioritize analysis tasks

---

## 📋 Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| **macOS** | ✅ Full Support | Native titlebar, dark mode |
| **Windows** | ✅ Full Support | Windows 10/11 |
| **Linux** | ✅ Full Support | Ubuntu 20.04+, Fedora 35+ |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or later
- pip (Python package manager)

### Installation

#### Option 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/Bracken-Team/Volari.git
cd Volari

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: Install as Package

```bash
pip install volari
```

### Launch the GUI

```bash
# From source
python volatility_gui/main.py

# Or if installed as package
volari
```

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
# VirusTotal API Key (required for malware scanning)
VIRUSTOTAL_API_KEY=your_api_key_here

# Logging level (DEBUG, INFO, WARNING, ERROR)
VOLARI_LOG_LEVEL=INFO

# Theme preference (dark, light, system)
VOLARI_THEME=dark
```

### Settings

Access Settings via **Volari → Settings** (macOS) or **File → Settings**.

| Setting | Description |
|---------|-------------|
| Theme | Dark, Light, or System |
| VirusTotal API Key | For malware scanning |
| Analyst Name | For PDF report headers |

---

## 🖼️ Screenshots

### Process Analysis
![Process Tab](docs/screenshots/process_tab.png)
*Placeholder - add process tab screenshot*

### Timeline View
![Timeline](docs/screenshots/timeline.png)
*Placeholder - add timeline screenshot*

### Investigation Queue
![Queue](docs/screenshots/queue.png)
*Placeholder - add queue screenshot*

---

## 📖 Documentation

Full documentation available in the [docs/](docs/) folder:

- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Configuration](docs/configuration.md)
- [Developer Guide](docs/developer_guide.md)
- [Changelog](docs/changelog.md)

---

## 🔧 Troubleshooting

### Qt/PyQt6 Issues

**Problem:** `ModuleNotFoundError: No module named 'PyQt6'`

```bash
pip install PyQt6>=6.0.0
```

**Problem:** Font rendering issues on Linux

```bash
sudo apt install libxcb-xinerama0
```

### Plugin Loading

**Problem:** Plugins not loading

1. Ensure Volatility 3 is installed: `pip install -e .`
2. Check symbol tables are downloaded
3. Verify Python path includes project root

### macOS Issues

**Problem:** App shows "Damaged" warning

```bash
xattr -cr /path/to/Volari.app
```

**Problem:** Dark mode not applying

Ensure PyObjC is installed:
```bash
pip install pyobjc-core pyobjc-framework-Cocoa
```

### Memory/Performance

**Problem:** High memory usage during analysis

- Use the Queue system to limit concurrent plugins
- Clear completed tasks periodically
- Restart app between large analyses

---

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/volatilityfoundation/volatility3.git
cd volatility3
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pip install -r requirements.txt
```

### Run Tests

```bash
pytest tests/ -v
```

### Lint Code

```bash
ruff check volatility_gui/
```

### Build Standalone App

```bash
# macOS
pyinstaller volari.spec --clean --noconfirm

# Output: dist/Volari.app
```

---

## 📄 License

Volatility Software License (VSL) - See [LICENSE.txt](LICENSE.txt)

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

---

## 📞 Contact

- **Volatility Foundation**: https://www.volatilityfoundation.org
- **Slack**: https://www.volatilityfoundation.org/slack
- **Issues**: https://github.com/volatilityfoundation/volatility3/issues
