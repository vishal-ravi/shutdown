# System Monitor & Crash Logger

A continuous background monitoring script for Ubuntu systems experiencing random shutdowns, freezes, or unexplained crashes. Captures comprehensive system state every 5 seconds to help diagnose root causes.

## Quick Start

```bash
chmod +x system_monitor.sh

# Start monitoring (runs in background)
./system_monitor.sh

# Check status
./system_monitor.sh --status

# Stop monitoring
./system_monitor.sh --stop

# Generate analysis report
./system_monitor.sh --report
```

## GUI Application

A PyQt5 desktop dashboard is included for visual monitoring.

```bash
# Launch the GUI
./launch_gui.sh

# Or run directly
python3 system_monitor_gui.py
```

### GUI Features

| Tab | Description |
|-----|-------------|
| **Dashboard** | Real-time CPU, memory, swap, disk, temperature, uptime stats with progress bars |
| **Controls** | Start/Stop monitor, view script info, log file overview |
| **Kernel** | Browse and export dmesg, hardware error logs |
| **System** | Browse journalctl, syslog, failed services |
| **Hardware** | CPU, RAM, disk, temperature, GPU logs |
| **Power** | Power supply status, shutdown/reboot history |
| **Network** | Interface status, active connections |
| **Processes** | Top consumers, zombie processes |
| **Snapshots** | System info, segfaults, MCE, PCI/USB errors |
| **Report** | Generate and export full analysis report |

### GUI Controls

| Shortcut | Action |
|----------|--------|
| `F5` | Start monitoring |
| `Shift+F5` | Stop monitoring |
| `F6` | Check status |
| `F7` | Generate report |
| `Ctrl+1-9,0` | Switch tabs |
| `Ctrl+E` | Export all logs |
| `Ctrl+Q` | Quit |

## What It Captures

| Category | Directory | Details |
|----------|-----------|---------|
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

Edit the variables at the top of the script:

```bash
INTERVAL=5                          # Seconds between captures (default: 5)
MAX_LOG_SIZE_MB=500                 # Max size per file before rotation
MAX_LOG_FILES=10                    # Max rotated files per type
```

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

To start the monitor automatically on every boot:

### Option 1: Systemd Service

```bash
sudo tee /etc/systemd/system/system-monitor.service << 'EOF'
[Unit]
Description=System Monitor and Crash Logger
After=multi-user.target

[Service]
Type=forking
ExecStart=/home/vishal/Pictures/System_down/system_monitor.sh
PIDFile=/home/vishal/Pictures/System_down/.monitor.pid
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
@reboot /home/vishal/Pictures/System_down/system_monitor.sh
```

## Dependencies

**Required:** `bash`, `ps`, `free`, `df`, `uptime`, `mkdir`, `cat`, `tail`

**Optional (for more detailed logs):**

```bash
# Install lm-sensors for temperature monitoring
sudo apt install lm-sensors
sudo sensors-detect

# Install smartmontools for disk health
sudo apt install smartmontools

# NVIDIA GPU users (usually pre-installed)
nvidia-smi
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

## License

Free to use and modify.
# shutdown
