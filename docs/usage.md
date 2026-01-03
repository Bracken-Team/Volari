# Usage Guide

## Launching Volari

```bash
# From source
python volatility_gui/main.py

# If installed as package
volari
```

## Loading a Memory Dump

1. Click **File → Open Memory Dump** or press `Cmd+O` (macOS) / `Ctrl+O`
2. Select your memory dump file (.vmem, .dmp, .raw, .img)
3. Wait for automatic OS detection

## Analysis Tabs

### OS Info
Click **Get OS Info** to retrieve system information including:
- Windows version and build
- Kernel information
- Boot time and system time

### Processes
Analyze running processes:
- View process tree
- Dump process memory
- Calculate file hashes
- Send to VirusTotal

### Network
View network connections and listening ports.

### Registry
Browse Windows registry hives:
- Hive Scan
- Hive List
- Print Key

### Files
List files in memory with extraction capability.

### Malware
Scan for indicators of compromise:
- Hollowed processes
- Suspicious imports
- Hidden modules

### Timeline
Visualize events chronologically with interactive charts.

### IOC Checker
Load and scan IOC files (STIX, OpenIOC, custom JSON).

### VirusTotal
Scan hashes against VirusTotal database.

## Auto-Investigation

Click **Auto Investigate** to queue essential plugins automatically:
1. OS Info
2. Process List
3. Network Connections
4. Registry Hives

## Investigation Queue

The queue panel shows all running and pending tasks:
- **Pause/Resume** individual tasks
- **Prioritize** tasks
- **Clear completed** to free memory

## Generating Reports

1. Run desired analyses
2. Click **File → Export Report**
3. Configure report options
4. Save as PDF

## Keyboard Shortcuts

| Action | macOS | Windows/Linux |
|--------|-------|---------------|
| Open File | Cmd+O | Ctrl+O |
| Settings | Cmd+, | Ctrl+, |
| Export Report | Cmd+E | Ctrl+E |
| Show Logs | Cmd+Shift+L | Ctrl+Shift+L |
| Show Queue | Cmd+Shift+Q | Ctrl+Shift+Q |
| Tab 1-9 | Cmd+1-9 | Ctrl+1-9 |
