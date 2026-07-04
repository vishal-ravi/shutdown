#!/usr/bin/env bash

# ============================================================================
# System Monitor & Crash Logger
# ============================================================================
# Continuously monitors and logs system state to diagnose random
# shutdowns, freezes, and power issues on Ubuntu systems.
#
# Usage:
#   ./system_monitor.sh              # Start monitoring
#   ./system_monitor.sh --status     # Check if running
#   ./system_monitor.sh --stop       # Stop monitoring
#   ./system_monitor.sh --report     # Generate analysis report
#
# Logs are saved to: ~/SystemMonitorLogs/
# ============================================================================

# ----- Configuration -----
LOG_DIR="${HOME}/SystemMonitorLogs"
INTERVAL=5
MAX_LOG_SIZE_MB=500
MAX_LOG_FILES=10
PID_FILE="${LOG_DIR}/.monitor.pid"
LOCK_FILE="/tmp/system_monitor.lock"

# ----- Colors -----
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; NC='\033[0m'

# ----- Utility Functions -----
log_msg() {
    local level="$1"; shift
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    case "$level" in
        INFO)  echo -e "${GREEN}[INFO]${NC}  ${ts} - $*" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC}  ${ts} - $*" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} ${ts} - $*" ;;
        *)     echo -e "${ts} - $*" ;;
    esac
}

check_dependencies() {
    local missing=()
    for dep in ps free df uptime date mkdir cat tail; do
        command -v "$dep" &>/dev/null || missing+=("$dep")
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        log_msg ERROR "Missing required commands: ${missing[*]}"
        exit 1
    fi
}

setup_log_dir() {
    mkdir -p "${LOG_DIR}/kernel"
    mkdir -p "${LOG_DIR}/system"
    mkdir -p "${LOG_DIR}/hardware"
    mkdir -p "${LOG_DIR}/power"
    mkdir -p "${LOG_DIR}/network"
    mkdir -p "${LOG_DIR}/processes"
    mkdir -p "${LOG_DIR}/snapshots"
}

acquire_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        local existing_pid
        existing_pid=$(cat "$LOCK_FILE" 2>/dev/null || true)
        if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
            log_msg ERROR "Monitor already running with PID ${existing_pid}"
            exit 1
        else
            log_msg WARN "Stale lock file found. Removing..."
            rm -f "$LOCK_FILE"
        fi
    fi
    echo $$ > "$LOCK_FILE"
    echo $$ > "$PID_FILE"
}

release_lock() {
    rm -f "$LOCK_FILE" "$PID_FILE"
}

# ----- Log Rotation -----
rotate_log() {
    local logfile="$1"
    [[ ! -f "$logfile" ]] && return 0

    local size_bytes
    size_bytes=$(wc -c < "$logfile" 2>/dev/null || echo 0)
    local max_bytes=$((MAX_LOG_SIZE_MB * 1024 * 1024))

    if [[ "$size_bytes" -ge "$max_bytes" ]]; then
        local dir base ext
        dir=$(dirname "$logfile")
        base=$(basename "$logfile")
        if [[ "$base" == *.* ]]; then
            ext=".${base##*.}"
            base="${base%.*}"
        else
            ext=""
        fi

        for ((i = MAX_LOG_FILES - 1; i >= 1; i--)); do
            local src="${dir}/${base}$((i-1))${ext}"
            local dst="${dir}/${base}${i}${ext}"
            [[ -f "$src" ]] && mv "$src" "$dst"
        done

        mv "$logfile" "${dir}/${base}0${ext}"
        touch "$logfile"
        log_msg INFO "Rotated: ${logfile}"
    fi
}

# ----- Capture Functions -----

capture_kernel_messages() {
    local outfile="${LOG_DIR}/kernel/dmesg_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    echo "===== dmesg capture @ $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$outfile"
    dmesg --time-format iso >> "$outfile" 2>/dev/null || dmesg >> "$outfile" 2>/dev/null || true
    echo "" >> "$outfile"
}

capture_journalctl() {
    local outfile="${LOG_DIR}/system/journal_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    echo "===== journalctl capture @ $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$outfile"
    journalctl --since "5 seconds ago" --no-pager -q >> "$outfile" 2>/dev/null || true
    echo "" >> "$outfile"
}

capture_syslog() {
    local outfile="${LOG_DIR}/system/syslog_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    echo "===== syslog tail @ $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$outfile"
    tail -n 50 /var/log/syslog >> "$outfile" 2>/dev/null || true
    echo "" >> "$outfile"
}

capture_hardware_temps() {
    local outfile="${LOG_DIR}/hardware/temperatures_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    {
        echo "===== Hardware temps @ $(date '+%Y-%m-%d %H:%M:%S') ====="
        if command -v sensors &>/dev/null; then
            sensors 2>/dev/null || echo "(sensors returned error)"
        else
            echo "(lm-sensors not installed)"
        fi
        echo ""
        echo "--- Thermal Zones ---"
        for zone in /sys/class/thermal/thermal_zone*/; do
            [[ -d "$zone" ]] || continue
            local ttype temp
            ttype=$(cat "${zone}/type" 2>/dev/null || echo "unknown")
            temp=$(cat "${zone}/temp" 2>/dev/null || echo "N/A")
            if [[ "$temp" != "N/A" ]]; then
                echo "${ttype}: $((temp / 1000))°C"
            fi
        done
        echo ""
    } >> "$outfile"
}

capture_cpu_info() {
    local outfile="${LOG_DIR}/hardware/cpu_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    {
        echo "===== CPU info @ $(date '+%Y-%m-%d %H:%M:%S') ====="
        echo "--- Load Average ---"
        uptime
        echo ""
        echo "--- CPU Usage (top 10) ---"
        ps -eo pid,user,%cpu,%mem,etime,comm --sort=-%cpu | head -n 11
        echo ""
        echo "--- CPU Frequency ---"
        for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
            [[ -f "$cpu" ]] || continue
            local freq
            freq=$(cat "$cpu" 2>/dev/null || echo "N/A")
            echo "$(dirname "$cpu" | xargs basename): ${freq} kHz"
        done 2>/dev/null || echo "(N/A)"
        echo ""
    } >> "$outfile"
}

capture_memory_info() {
    local outfile="${LOG_DIR}/hardware/memory_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    {
        echo "===== Memory info @ $(date '+%Y-%m-%d %H:%M:%S') ====="
        free -h
        echo ""
        echo "--- Swap Usage ---"
        swapon --show 2>/dev/null || echo "(no swap)"
        echo ""
        echo "--- OOM Killer Events (last 5 min) ---"
        dmesg 2>/dev/null | grep -i "out of memory" | tail -n 5 || echo "(none found)"
        echo ""
        echo "--- Top Memory Consumers ---"
        ps -eo pid,user,%mem,rss,comm --sort=-%mem | head -n 11
        echo ""
    } >> "$outfile"
}

capture_disk_info() {
    local outfile="${LOG_DIR}/hardware/disk_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    {
        echo "===== Disk info @ $(date '+%Y-%m-%d %H:%M:%S') ====="
        echo "--- Disk Usage ---"
        df -h 2>/dev/null
        echo ""
        echo "--- I/O Stats ---"
        cat /proc/diskstats 2>/dev/null | head -n 10 || true
        echo ""
        if command -v iostat &>/dev/null; then
            echo "--- iostat ---"
            iostat -x 1 1 2>/dev/null || true
            echo ""
        fi
        echo "--- Mount Points ---"
        mount | grep -E "^/dev" || true
        echo ""
    } >> "$outfile"
}

capture_power_events() {
    local outfile="${LOG_DIR}/power/power_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    {
        echo "===== Power events @ $(date '+%Y-%m-%d %H:%M:%S') ====="
        if [[ -d /sys/class/power_supply ]]; then
            echo "--- Power Supply ---"
            for supply in /sys/class/power_supply/*/; do
                [[ -d "$supply" ]] || continue
                echo "[$(basename "$supply")]"
                for f in type status online capacity voltage_now current_now; do
                    [[ -f "${supply}${f}" ]] && echo "  ${f}: $(cat "${supply}${f}" 2>/dev/null)"
                done
            done
            echo ""
        fi
        if command -v upsc &>/dev/null; then
            echo "--- UPS Status ---"
            upsc 2>/dev/null || echo "(no UPS found)"
            echo ""
        fi
        echo "--- Recent Shutdown/Reboot History ---"
        last -x shutdown reboot 2>/dev/null | head -n 10 || echo "(unavailable)"
        echo ""
    } >> "$outfile"
}

capture_network_info() {
    local outfile="${LOG_DIR}/network/network_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    {
        echo "===== Network info @ $(date '+%Y-%m-%d %H:%M:%S') ====="
        if command -v ip &>/dev/null; then
            ip -brief addr show 2>/dev/null
            echo ""
            ip -brief link show 2>/dev/null
        else
            ifconfig 2>/dev/null || echo "(ip command not available)"
        fi
        echo ""
        echo "--- Active Connections (top 10) ---"
        ss -tunap 2>/dev/null | head -n 11 || echo "(unavailable)"
        echo ""
    } >> "$outfile"
}

capture_process_info() {
    local outfile="${LOG_DIR}/processes/processes_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    {
        echo "===== Process info @ $(date '+%Y-%m-%d %H:%M:%S') ====="
        echo "--- System Uptime ---"
        uptime -p 2>/dev/null || uptime
        echo ""
        echo "--- Running Processes ---"
        ps aux --sort=-%cpu | head -n 21
        echo ""
        echo "--- Zombie Processes ---"
        ps aux | awk '$8 ~ /Z/ {print}' 2>/dev/null || echo "(none)"
        echo ""
    } >> "$outfile"
}

capture_snapshots() {
    local outfile="${LOG_DIR}/snapshots/snapshot_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    {
        echo "===== System snapshot @ $(date '+%Y-%m-%d %H:%M:%S') ====="
        echo "--- Kernel Version ---"
        uname -a
        echo ""
        echo "--- Ubuntu Version ---"
        cat /etc/os-release 2>/dev/null || true
        echo ""
        echo "--- Segmentation Faults (recent) ---"
        dmesg 2>/dev/null | grep -i "segfault" | tail -n 5 || echo "(none)"
        echo ""
        echo "--- MCE / Hardware Errors (recent) ---"
        dmesg 2>/dev/null | grep -iE "mce|hardware error|machine check" | tail -n 5 || echo "(none)"
        echo ""
        echo "--- PCI / USB Errors ---"
        dmesg 2>/dev/null | grep -iE "pci|usb" | grep -iE "error|fail|reset" | tail -n 10 || echo "(none)"
        echo ""
    } >> "$outfile"
}

capture_nvidia_gpu() {
    command -v nvidia-smi &>/dev/null || return 0
    local outfile="${LOG_DIR}/hardware/gpu_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    {
        echo "===== GPU info @ $(date '+%Y-%m-%d %H:%M:%S') ====="
        nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv 2>/dev/null || true
        echo ""
        nvidia-smi 2>/dev/null || true
        echo ""
    } >> "$outfile"
}

capture_systemctl_status() {
    local outfile="${LOG_DIR}/system/services_$(date '+%Y%m%d').log"
    rotate_log "$outfile"
    {
        echo "===== Service status @ $(date '+%Y-%m-%d %H:%M:%S') ====="
        echo "--- Failed Services ---"
        systemctl --failed --no-pager 2>/dev/null || true
        echo ""
        echo "--- Recent Service Logs ---"
        journalctl --since "5 seconds ago" -u systemd --no-pager -q 2>/dev/null || true
        echo ""
    } >> "$outfile"
}

# ----- Master Capture Cycle -----
capture_all() {
    local cycle_start
    cycle_start=$(date +%s)

    capture_kernel_messages
    capture_journalctl
    capture_syslog
    capture_hardware_temps
    capture_cpu_info
    capture_memory_info
    capture_disk_info
    capture_power_events
    capture_network_info
    capture_process_info
    capture_snapshots
    capture_nvidia_gpu
    capture_systemctl_status

    local cycle_end
    cycle_end=$(date +%s)
    echo "$(date '+%Y-%m-%d %H:%M:%S') | cycle_duration=$((cycle_end - cycle_start))s" >> "${LOG_DIR}/.capture_log"
}

# ----- Report Generation -----
generate_report() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  System Monitor Analysis Report${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${GREEN}Log directory:${NC} ${LOG_DIR}"
    echo ""

    local total_files total_size
    total_files=$(find "${LOG_DIR}" -name "*.log" -type f 2>/dev/null | wc -l)
    total_size=$(du -sh "${LOG_DIR}" 2>/dev/null | cut -f1)
    echo -e "${GREEN}Total log files:${NC} ${total_files}"
    echo -e "${GREEN}Total log size:${NC}  ${total_size}"
    echo ""

    if [[ -f "${LOG_DIR}/.capture_log" ]]; then
        local first last count
        first=$(head -n 1 "${LOG_DIR}/.capture_log" | cut -d'|' -f1)
        last=$(tail -n 1 "${LOG_DIR}/.capture_log" | cut -d'|' -f1)
        count=$(wc -l < "${LOG_DIR}/.capture_log")
        echo -e "${GREEN}Monitoring started:${NC} ${first}"
        echo -e "${GREEN}Last capture:${NC}       ${last}"
        echo -e "${GREEN}Total captures:${NC}     ${count}"
    fi
    echo ""

    echo -e "${YELLOW}--- Recent Critical Errors ---${NC}"
    local dmesg_file="${LOG_DIR}/kernel/dmesg_$(date '+%Y%m%d').log"
    if [[ -f "$dmesg_file" ]]; then
        grep -iE "error|fail|critical|panic|oops|bug|warn" "$dmesg_file" 2>/dev/null | tail -n 50
    fi
    echo ""

    echo -e "${YELLOW}--- Temperature Readings ---${NC}"
    local temp_file="${LOG_DIR}/hardware/temperatures_$(date '+%Y%m%d').log"
    [[ -f "$temp_file" ]] && grep -E "°C" "$temp_file" 2>/dev/null | tail -n 20
    echo ""

    echo -e "${YELLOW}--- Out of Memory Events ---${NC}"
    grep -rl "out of memory" "${LOG_DIR}/" 2>/dev/null | head -n 5 || echo "(none found)"
    echo ""

    echo -e "${YELLOW}--- System Shutdown/Reboot History ---${NC}"
    last -x shutdown reboot 2>/dev/null | head -n 15 || echo "(unavailable)"
    echo ""

    echo -e "${YELLOW}--- Disk Space ---${NC}"
    df -h 2>/dev/null
    echo ""

    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  Key Log File Locations${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo "  Kernel/dmesg:    ${LOG_DIR}/kernel/"
    echo "  System logs:     ${LOG_DIR}/system/"
    echo "  Hardware temps:  ${LOG_DIR}/hardware/"
    echo "  Power events:    ${LOG_DIR}/power/"
    echo "  Network:         ${LOG_DIR}/network/"
    echo "  Processes:       ${LOG_DIR}/processes/"
    echo ""
}

# ----- Signal Handlers -----
_stopped=0
cleanup() {
    [[ $_stopped -eq 1 ]] && return
    _stopped=1
    log_msg INFO "Stopping System Monitor..."
    release_lock
    log_msg INFO "Logs saved to: ${LOG_DIR}"
    exit 0
}

# ----- Main -----
main() {
    local cmd="${1:-}"

    case "$cmd" in
        --status|-s)
            if [[ -f "$PID_FILE" ]]; then
                local pid
                pid=$(cat "$PID_FILE")
                if kill -0 "$pid" 2>/dev/null; then
                    echo -e "${GREEN}Monitor is RUNNING${NC} (PID: ${pid})"
                else
                    echo -e "${RED}Monitor PID exists but process is DEAD${NC}"
                    rm -f "$PID_FILE" "$LOCK_FILE"
                fi
            else
                echo -e "${YELLOW}Monitor is NOT running${NC}"
            fi
            exit 0
            ;;
        --stop|-k)
            if [[ -f "$PID_FILE" ]]; then
                local pid
                pid=$(cat "$PID_FILE")
                if kill -0 "$pid" 2>/dev/null; then
                    kill "$pid"
                    echo -e "${GREEN}Stopped monitor (PID: ${pid})${NC}"
                else
                    echo -e "${YELLOW}Monitor was not running (stale PID file)${NC}"
                    rm -f "$PID_FILE" "$LOCK_FILE"
                fi
            else
                echo -e "${YELLOW}Monitor is NOT running${NC}"
            fi
            exit 0
            ;;
        --report|-r)
            generate_report
            exit 0
            ;;
        --help|-h)
            echo "Usage: $0 [OPTION]"
            echo ""
            echo "Options:"
            echo "  (no args)    Start continuous monitoring in background"
            echo "  --status     Check if monitor is running"
            echo "  --stop       Stop the monitor"
            echo "  --report     Generate analysis report"
            echo "  --help       Show this help"
            echo ""
            echo "Log directory: ${LOG_DIR}"
            exit 0
            ;;
    esac

    # Setup
    log_msg INFO "Starting System Monitor v1.0"
    check_dependencies
    setup_log_dir
    acquire_lock

    trap cleanup EXIT
    trap 'log_msg WARN "Received SIGHUP - ignoring"' HUP
    trap cleanup TERM
    trap cleanup INT

    log_msg INFO "Monitor started (PID: $$)"
    log_msg INFO "Capturing system state every ${INTERVAL} seconds"
    log_msg INFO "Logs directory: ${LOG_DIR}"

    # Initial full capture
    capture_all

    # Continuous monitoring loop
    while true; do
        sleep "$INTERVAL" &
        wait $! 2>/dev/null || true

        if [[ ! -f "$LOCK_FILE" ]]; then
            log_msg INFO "Lock file removed, stopping..."
            break
        fi

        capture_all
    done

    cleanup
}

main "$@"
