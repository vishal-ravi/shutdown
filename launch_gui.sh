#!/usr/bin/env bash
# Launcher for System Monitor GUI
# Checks for PyQt5 and installs if missing

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check for Python3
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install with: sudo apt install python3"
    exit 1
fi

# Check for PyQt5
if ! python3 -c "from PyQt5.QtWidgets import QApplication" 2>/dev/null; then
    echo "PyQt5 not found. Installing..."
    pip3 install PyQt5 2>/dev/null || pip install PyQt5 2>/dev/null || {
        echo "ERROR: Failed to install PyQt5. Install manually:"
        echo "  sudo apt install python3-pyqt5"
        echo "  pip3 install PyQt5"
        exit 1
    }
fi

# Launch the GUI
exec python3 "${SCRIPT_DIR}/system_monitor_gui.py" "$@"
