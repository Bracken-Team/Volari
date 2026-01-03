# Configuration Guide

## Environment Variables

Volari uses environment variables for sensitive configuration.

### Setup

```bash
cp .env.example .env
```

### Available Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VIRUSTOTAL_API_KEY` | API key for VirusTotal scanning | (none) |
| `VOLARI_LOG_LEVEL` | Logging verbosity | `INFO` |
| `VOLARI_THEME` | UI theme | `dark` |
| `VOLARI_OUTPUT_DIR` | Default export directory | (user's home) |

### Example .env

```ini
VIRUSTOTAL_API_KEY=your_64_character_api_key_here
VOLARI_LOG_LEVEL=DEBUG
VOLARI_THEME=dark
```

## GUI Settings

Access via **Volari → Settings** (macOS) or **File → Settings**.

### Application Settings

- **Theme**: Dark, Light, or System
- **Font Size**: Adjust UI text size
- **Auto-load symbols**: Automatically download missing symbol tables

### Analyst Settings

- **Analyst Name**: Your name for report headers
- **Organization**: Your organization name
- **Contact Info**: Email/phone for reports

### VirusTotal Settings

- **API Key**: Your VirusTotal API key
- **Rate Limit**: Requests per minute (free tier: 4)

## Settings Storage

Settings are stored in:

| Platform | Location |
|----------|----------|
| macOS | `~/Library/Application Support/Volari/settings.json` |
| Windows | `%APPDATA%\Volari\settings.json` |
| Linux | `~/.config/Volari/settings.json` |

## Plugin Configuration

Volatility 3 plugins are configured via command-line arguments translated to GUI options.

Common plugin options can be set in the Settings dialog under **Plugin Defaults**.
