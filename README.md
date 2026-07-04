# System Monitor & Crash Logger

> A comprehensive system monitoring and crash logging solution for Ubuntu/Linux systems experiencing random shutdowns, freezes, or unexplained crashes.

[![GitHub stars](https://img.shields.io/github/stars/vishal-ravi/shutdown.svg?style=social)](https://github.com/vishal-ravi/shutdown/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/vishal-ravi/shutdown.svg)](https://github.com/vishal-ravi/shutdown/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Ubuntu%20%7C%20Linux-blue.svg)](https://ubuntu.com)

## Overview

System Monitor & Crash Logger is a powerful background monitoring tool that captures comprehensive system state every 5 seconds to help diagnose root causes of random shutdowns, freezes, and crashes. It includes both a CLI tool and a modern PyQt5 GUI dashboard.

**Perfect for:**
- Diagnosing random system shutdowns
- Monitoring hardware health
- Tracking temperature spikes
- Logging kernel panics and OOM events
- Power supply issue detection

## Features

### Core Monitoring
- **Real-time System Stats** - CPU, memory, swap, disk usage monitoring
- **Temperature Tracking** - CPU/GPU thermal zone readings
- **Power Event Logging** - AC adapter, battery status, UPS monitoring
- **Kernel Message Capture** - dmesg, segfaults, MCE errors, hardware failures
- **Network Monitoring** - Interface status, active connections
- **Process Tracking** - Top consumers, zombie detection

### Advanced Capabilities
- **Automatic Log Rotation** - Prevents disk fill-up (500MB per file, 10 rotations)
- **Background Operation** - Minimal resource footprint
- **Analysis Reports** - One-click diagnostic reports
- **Boot Persistence** - Systemd service and cron options

### GUI Dashboard (PyQt5)
- **Real-time Dashboard** - Live CPU, memory, swap, disk, temperature stats
- **Interactive Log Viewer** - Browse and export logs by category
- **One-click Reports** - Generate comprehensive diagnostic reports
- **Modern UI** - Professional dark theme with progress bars
- **Keyboard Shortcuts** - F5 (start), Shift+F5 (stop), Ctrl+1-9 (tabs)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/vishal-ravi/shutdown.git
cd shutdown

# Make scripts executable
chmod +x system_monitor.sh launch_gui.sh
```

### CLI Usage

```bash
# Start monitoring (runs in background)
./system_monitor.sh

# Check if monitor is running
./system_monitor.sh --status

# Stop monitoring
./system_monitor.sh --stop

# Generate analysis report
./system_monitor.sh --report

# Show help
./system_monitor.sh --help
```

### GUI Usage

```bash
# Launch the GUI dashboard
./launch_gui.sh

# Or run directly
python3 system_monitor_gui.py
```

## What Gets Captured

| Category | Directory | Data Captured |
|----------|-----------|---------------|
| **Kernel** | `kernel/` | dmesg, hardware errors, segfaults, MCE events |
| **System** | `system/` | journalctl, syslog, failed systemd services |
| **Hardware** | `hardware/` | CPU usage/frequency, RAM, disk I/O, temperatures, GPU (NVIDIA) |
| **Power** | `power/` | AC adapter, battery status, UPS, shutdown/reboot history |
| **Network** | `network/` | Interfaces, active connections, socket stats |
| **Processes** | `processes/` | Top CPU/RAM consumers, zombie processes, FD leaks |
| **Snapshots** | `snapshots/` | Kernel version, OS info, recent critical errors |

## Log Structure

```
~/SystemMonitorLogs/
├── kernel/
│   └── dmesg_20260605.log
├── system/
│   ├── journal_20260605.log
│   ├── syslog_20260605.log
│   └── services_20260605.log
├── hardware/
│   ├── temperatures_20260605.log
│   ├── cpu_20260605.log
│   ├── memory_20260605.log
│   ├── disk_20260605.log
│   └── gpu_20260605.log
├── power/
│   └── power_20260605.log
├── network/
│   └── network_20260605.log
├── processes/
│   └── processes_20260605.log
└── snapshots/
    └── snapshot_20260605.log
```

## Configuration

Edit these variables at the top of `system_monitor.sh`:

```bash
INTERVAL=5                          # Seconds between captures (default: 5)
MAX_LOG_SIZE_MB=500                 # Max size per file before rotation
MAX_LOG_FILES=10                    # Max rotated files per type
```

## GUI Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Start monitoring |
| `Shift+F5` | Stop monitoring |
| `F6` | Check status |
| `F7` | Generate report |
| `Ctrl+1-9,0` | Switch tabs (Dashboard=1, Controls=2, ..., Report=0) |
| `Ctrl+E` | Export all logs |
| `Ctrl+Q` | Quit |

## Log Rotation

Each log file is automatically rotated when it reaches `MAX_LOG_SIZE_MB` (default 500 MB). Up to `MAX_LOG_FILES` (default 10) rotated copies are kept per file type, named `filename0.log`, `filename1.log`, etc.

## Report Output

The `--report` flag generates a summary including:

- Total log files and disk usage
- Monitoring duration and capture count
- Recent critical errors from dmesg
- Temperature readings
- Out-of-memory events
- Power supply status
- System shutdown/reboot history
- Current disk space

## Diagnosing Random Shutdowns

When your system crashes or freezes, run the report and look for:

| Symptom | Check these files |
|---------|-------------------|
| **Thermal shutdown** | `hardware/temperatures_*.log` — look for temps above 90°C |
| **OOM crash** | `hardware/memory_*.log` — check for "out of memory" entries |
| **Kernel panic** | `kernel/dmesg_*.log` — grep for `panic`, `oops`, `bug` |
| **Hardware failure** | `kernel/dmesg_*.log` — grep for `mce`, `hardware error`, `segfault` |
| **Power loss** | `power/power_*.log` — check AC adapter / battery status |
| **Disk failure** | `hardware/disk_*.log` — check for I/O errors |
| **Driver crash** | `kernel/dmesg_*.log` — grep for `reset`, `timeout`, `error` |

### Useful Manual Commands

```bash
# See all logs since last boot
journalctl -b

# Search for kernel errors
dmesg | grep -iE "error|fail|panic|oops|mce|segfault"

# Check system temperatures
sensors

# Check disk health
sudo smartctl -a /dev/sda

# View power events
last -x shutdown reboot

# Monitor real-time system state
htop
```

## Run at Boot (Persistent Monitoring)

### Option 1: Systemd Service (Recommended)

```bash
sudo tee /etc/systemd/system/system-monitor.service << 'EOF'
[Unit]
Description=System Monitor and Crash Logger
After=multi-user.target

[Service]
Type=forking
ExecStart=/path/to/system_monitor.sh
PIDFile=/path/to/SystemMonitorLogs/.monitor.pid
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now system-monitor.service
```

### Option 2: Cron

```bash
# Open crontab
crontab -e

# Add this line to start at boot
@reboot /path/to/system_monitor.sh
```

## Dependencies

### Required (CLI)

```bash
# Core utilities (pre-installed on most systems)
bash ps free df uptime mkdir cat tail
```

### Optional (Enhanced Logging)

```bash
# Temperature monitoring
sudo apt install lm-sensors
sudo sensors-detect

# Disk health monitoring
sudo apt install smartmontools

# NVIDIA GPU monitoring (usually pre-installed)
nvidia-smi
```

### GUI Requirements

```bash
# Python 3
sudo apt install python3

# PyQt5
sudo apt install python3-pyqt5
# OR
pip3 install PyQt5
```

## Uninstall

```bash
# Stop the monitor
./system_monitor.sh --stop

# Remove logs
rm -rf ~/SystemMonitorLogs

# If you created a systemd service
sudo systemctl disable --now system-monitor.service
sudo rm /etc/systemd/system/system-monitor.service
sudo systemctl daemon-reload
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Vishal Ravi** - System Administrator

## Acknowledgments

- Built for Ubuntu/Linux systems experiencing random shutdowns
- Designed for hardware diagnostics and system troubleshooting
- Inspired by the need for comprehensive system monitoring tools

---

**Found this helpful?** Give it a ⭐ on GitHub!
