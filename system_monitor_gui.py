#!/usr/bin/env python3
"""
System Monitor GUI - Modern Professional Dashboard
"""

import sys, os, subprocess
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QTextEdit, QFrame, QGridLayout,
    QGroupBox, QSplitter, QAction, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QTextCursor, QColor


SCRIPT_DIR = Path(__file__).parent.resolve()
SCRIPT_PATH = SCRIPT_DIR / "system_monitor.sh"
LOG_DIR = Path.home() / "SystemMonitorLogs"
REFRESH_MS = 3000

ACCENT = "#2563eb"
ACCENT_DARK = "#1d4ed8"
ACCENT_LIGHT = "#dbeafe"
SUCCESS = "#16a34a"
SUCCESS_LIGHT = "#dcfce7"
DANGER = "#dc2626"
DANGER_LIGHT = "#fee2e2"
ORANGE = "#ea580c"
ORANGE_LIGHT = "#fff7ed"
PURPLE = "#7c3aed"
PURPLE_LIGHT = "#f5f3ff"
TEAL = "#0891b2"
TEAL_LIGHT = "#ecfeff"
GRAY_50 = "#f9fafb"
GRAY_100 = "#f3f4f6"
GRAY_200 = "#e5e7eb"
GRAY_300 = "#d1d5db"
GRAY_400 = "#9ca3af"
GRAY_500 = "#6b7280"
GRAY_600 = "#4b5563"
GRAY_700 = "#374151"
GRAY_800 = "#1f2937"
GRAY_900 = "#111827"
WHITE = "#ffffff"
BG = "#f0f2f5"


STYLE = """
* { font-family: 'Segoe UI', 'Ubuntu', 'Noto Sans', sans-serif; }

QMainWindow { background-color: %(bg)s; }

/* ---- Tab Widget ---- */
QTabWidget::pane {
    border: 1px solid %(gray300)s;
    background: %(white)s;
    border-radius: 0 0 12px 12px;
    margin-top: -1px;
}
QTabBar {
    background: transparent;
}
QTabBar::tab {
    background: %(gray100)s;
    color: %(gray500)s;
    padding: 11px 28px;
    margin-right: 2px;
    border: 1px solid %(gray300)s;
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-weight: 600;
    font-size: 13px;
    min-width: 110px;
}
QTabBar::tab:selected {
    background: %(white)s;
    color: %(accent)s;
    border-bottom: 3px solid %(accent)s;
    font-weight: 700;
}
QTabBar::tab:hover:!selected {
    background: %(gray200)s;
    color: %(gray700)s;
}

/* ---- Push Buttons ---- */
QPushButton {
    background: %(white)s;
    color: %(gray700)s;
    border: 1px solid %(gray300)s;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}
QPushButton:hover {
    background: %(gray50)s;
    border-color: %(gray400)s;
}
QPushButton:pressed {
    background: %(gray100)s;
}
QPushButton:disabled {
    background: %(gray50)s;
    color: %(gray300)s;
    border-color: %(gray200)s;
}
QPushButton#btnStart {
    background: %(success)s;
    color: %(white)s;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 14px 40px;
    border-radius: 10px;
}
QPushButton#btnStart:hover { background: #15803d; }
QPushButton#btnStart:disabled { background: %(gray200)s; color: %(gray400)s; }
QPushButton#btnStop {
    background: %(danger)s;
    color: %(white)s;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 14px 40px;
    border-radius: 10px;
}
QPushButton#btnStop:hover { background: #b91c1c; }
QPushButton#btnStop:disabled { background: %(gray200)s; color: %(gray400)s; }
QPushButton#btnAccent {
    background: %(accent)s;
    color: %(white)s;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 14px 40px;
    border-radius: 10px;
}
QPushButton#btnAccent:hover { background: %(accent_dark)s; }
QPushButton#btnSecondary {
    background: %(gray100)s;
    color: %(gray700)s;
    border: 1px solid %(gray300)s;
    font-size: 13px;
    padding: 10px 24px;
    border-radius: 8px;
}
QPushButton#btnSecondary:hover { background: %(gray200)s; }
QPushButton#btnSmall {
    background: %(white)s;
    color: %(gray600)s;
    border: 1px solid %(gray300)s;
    font-size: 12px;
    padding: 7px 18px;
    border-radius: 6px;
    min-height: 18px;
}
QPushButton#btnSmall:hover { background: %(gray50)s; border-color: %(gray400)s; }

/* ---- Text Edit ---- */
QTextEdit {
    background: %(white)s;
    color: %(gray800)s;
    border: 1px solid %(gray300)s;
    border-radius: 10px;
    padding: 12px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 12px;
    selection-background-color: %(accent_light)s;
    selection-color: %(accent_dark)s;
}

/* ---- Tables ---- */
QTableWidget {
    background: %(white)s;
    color: %(gray800)s;
    border: 1px solid %(gray300)s;
    border-radius: 10px;
    gridline-color: %(gray100)s;
    font-size: 13px;
    selection-background-color: %(accent_light)s;
    selection-color: %(accent)s;
    outline: none;
}
QTableWidget::item {
    padding: 10px 8px;
    border-bottom: 1px solid %(gray100)s;
}
QTableWidget::item:selected {
    background: %(accent_light)s;
    color: %(accent)s;
}
QTableWidget::item:hover {
    background: %(gray50)s;
}
QHeaderView::section {
    background: %(gray50)s;
    color: %(gray600)s;
    padding: 12px 10px;
    border: none;
    border-bottom: 2px solid %(gray200)s;
    border-right: 1px solid %(gray100)s;
    font-weight: 700;
    font-size: 11px;
}

/* ---- Group Box ---- */
QGroupBox {
    border: 1px solid %(gray200)s;
    border-radius: 12px;
    margin-top: 20px;
    padding: 24px 16px 16px 16px;
    font-weight: 700;
    font-size: 14px;
    color: %(accent)s;
    background: %(white)s;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 20px;
    padding: 0 10px;
}

/* ---- Progress Bar ---- */
QProgressBar {
    border: none;
    border-radius: 8px;
    background: %(gray100)s;
    text-align: right;
    padding-right: 12px;
    font-weight: 700;
    font-size: 12px;
    color: %(gray600)s;
    min-height: 26px;
    max-height: 26px;
}
QProgressBar::chunk {
    border-radius: 8px;
}

/* ---- Scrollbar ---- */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: %(gray300)s;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: %(gray400)s; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: %(gray300)s;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: %(gray400)s; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ---- Status Bar ---- */
QStatusBar {
    background: %(white)s;
    color: %(gray500)s;
    border-top: 1px solid %(gray200)s;
    font-size: 12px;
    padding: 6px 16px;
}

/* ---- Menu Bar ---- */
QMenuBar {
    background: %(white)s;
    color: %(gray700)s;
    border-bottom: 1px solid %(gray200)s;
    padding: 2px;
    font-size: 13px;
}
QMenuBar::item { padding: 8px 14px; border-radius: 6px; }
QMenuBar::item:selected { background: %(accent_light)s; color: %(accent)s; }
QMenu {
    background: %(white)s;
    color: %(gray700)s;
    border: 1px solid %(gray200)s;
    border-radius: 10px;
    padding: 8px 0;
}
QMenu::item {
    padding: 10px 32px;
    border-radius: 6px;
    margin: 2px 8px;
}
QMenu::item:selected { background: %(accent_light)s; color: %(accent)s; }
QMenu::separator { height: 1px; background: %(gray200)s; margin: 6px 12px; }

/* ---- Splitter ---- */
QSplitter::handle { background: %(gray200)s; width: 1px; }
QSplitter::handle:hover { background: %(accent)s; }
""" % {
    "bg": BG, "white": WHITE, "accent": ACCENT, "accent_dark": ACCENT_DARK,
    "accent_light": ACCENT_LIGHT, "success": SUCCESS, "danger": DANGER,
    "gray50": GRAY_50, "gray100": GRAY_100, "gray200": GRAY_200,
    "gray300": GRAY_300, "gray400": GRAY_400, "gray500": GRAY_500,
    "gray600": GRAY_600, "gray700": GRAY_700, "gray800": GRAY_800,
}


# ============================================================================
class Worker(QThread):
    done = pyqtSignal(str)
    err = pyqtSignal(str)
    def __init__(self, cmd, timeout=30):
        super().__init__()
        self.cmd, self.timeout = cmd, timeout
    def run(self):
        try:
            r = subprocess.run(self.cmd, shell=True, capture_output=True, text=True, timeout=self.timeout)
            self.done.emit((r.stdout + r.stderr).strip())
        except subprocess.TimeoutExpired:
            self.err.emit("Timed out")
        except Exception as e:
            self.err.emit(str(e))


# ============================================================================
class Card(QFrame):
    def __init__(self, title, value="—", subtitle="", color=ACCENT):
        super().__init__()
        self._color = color
        self.setFixedSize(280, 130)
        self.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {GRAY_200};
                border-radius: 14px;
                border-left: 4px solid {color};
            }}
            QFrame:hover {{
                border: 1px solid {GRAY_300};
                border-left: 4px solid {color};
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(2)

        t = QLabel(title)
        t.setStyleSheet(f"font-size:11px;font-weight:700;color:{GRAY_500};letter-spacing:1px;border:none;background:transparent;")
        self._val = QLabel(value)
        self._val.setStyleSheet(f"font-size:32px;font-weight:800;color:{color};border:none;background:transparent;")
        self._sub = QLabel(subtitle)
        self._sub.setStyleSheet(f"font-size:11px;color:{GRAY_400};border:none;background:transparent;")

        lay.addWidget(t)
        lay.addSpacing(4)
        lay.addWidget(self._val)
        lay.addWidget(self._sub)

    def set(self, v, sub=None):
        self._val.setText(str(v))
        if sub is not None:
            self._sub.setText(sub)


# ============================================================================
class Bar(QWidget):
    def __init__(self, label, color=ACCENT):
        super().__init__()
        self.setFixedHeight(34)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        self._lbl = QLabel(label)
        self._lbl.setFixedWidth(90)
        self._lbl.setStyleSheet(f"font-weight:700;font-size:13px;color:{GRAY_700};border:none;background:transparent;")
        lay.addWidget(self._lbl)

        c2 = QColor(color).lighter(135).name()
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(22)
        self._bar.setStyleSheet(f"""
            QProgressBar {{ border:none; border-radius:10px; background:{GRAY_100}; }}
            QProgressBar::chunk {{ border-radius:10px; background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {color}, stop:1 {c2}); }}
        """)
        lay.addWidget(self._bar, 1)

        self._pct = QLabel("0%")
        self._pct.setFixedWidth(48)
        self._pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._pct.setStyleSheet(f"font-weight:800;font-size:13px;color:{GRAY_700};border:none;background:transparent;")
        lay.addWidget(self._pct)

    def set(self, v):
        self._bar.setValue(int(v))
        self._pct.setText(f"{int(v)}%")


# ============================================================================
class LogView(QWidget):
    def __init__(self, cat):
        super().__init__()
        self.cat = cat
        self._file = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        top = QHBoxLayout()
        lbl = QLabel(cat.upper() + "  Logs")
        lbl.setStyleSheet(f"font-size:16px;font-weight:800;color:{ACCENT_DARK};border:none;background:transparent;")
        top.addWidget(lbl)
        top.addStretch()

        rb = QPushButton("Refresh")
        rb.setObjectName("btnSmall")
        rb.setFixedWidth(90)
        rb.clicked.connect(self.refresh)
        top.addWidget(rb)
        eb = QPushButton("Export")
        eb.setObjectName("btnSmall")
        eb.setFixedWidth(90)
        eb.clicked.connect(self.export)
        top.addWidget(eb)
        lay.addLayout(top)

        sp = QSplitter(Qt.Horizontal)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["File", "Size"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.currentCellChanged.connect(self._select)
        self.table.setMaximumWidth(300)
        self.table.setMinimumWidth(220)
        sp.addWidget(self.table)

        self.view = QTextEdit()
        self.view.setReadOnly(True)
        self.view.setLineWrapMode(QTextEdit.NoWrap)
        sp.addWidget(self.view)

        sp.setSizes([260, 900])
        lay.addWidget(sp)
        self.refresh()

    def _dir(self):
        return LOG_DIR / self.cat

    def refresh(self):
        d = self._dir()
        self.table.setRowCount(0)
        if not d.exists():
            return
        files = sorted(d.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
        self.table.setRowCount(len(files))
        for i, f in enumerate(files):
            it = QTableWidgetItem(f.name)
            it.setData(Qt.UserRole, str(f))
            sz = f.stat().st_size
            s = f"{sz/1024**2:.1f} MB" if sz > 1024**2 else (f"{sz/1024:.1f} KB" if sz > 1024 else f"{sz} B")
            si = QTableWidgetItem(s)
            si.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 0, it)
            self.table.setItem(i, 1, si)
        if files:
            self.table.selectRow(0)

    def _select(self, r, c, pr, pc):
        if r < 0:
            return
        it = self.table.item(r, 0)
        if it:
            self._file = Path(it.data(Qt.UserRole))
            try:
                with open(self._file, 'r', errors='replace') as f:
                    self.view.setPlainText(f.read())
                cur = self.view.textCursor()
                cur.movePosition(QTextCursor.End)
                self.view.setTextCursor(cur)
            except Exception as e:
                self.view.setPlainText(str(e))

    def export(self):
        if not self._file:
            return
        p, _ = QFileDialog.getSaveFileName(self, "Export", self._file.name, "Logs (*.log);;All (*)")
        if p:
            try:
                with open(self._file) as s, open(p, 'w') as d:
                    d.write(s.read())
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))


# ============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Monitor — Crash Logger & Diagnostics")
        self.resize(1460, 940)
        self.setMinimumSize(1200, 700)
        self._running = False
        self._pid = None
        self._build()
        self._menu()
        self.statusBar().showMessage("Ready")
        self._timers()
        self._check_status()
        self._refresh_dash()

    # ---- Build UI ----
    def _build(self):
        c = QWidget()
        self.setCentralWidget(c)
        root = QVBoxLayout(c)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._header())

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._dash(), "   Dashboard   ")
        self.tabs.addTab(self._ctrls(), "   Controls   ")
        for cat in ["kernel", "system", "hardware", "power", "network", "processes", "snapshots"]:
            self.tabs.addTab(LogView(cat), f"   {cat.capitalize()}   ")
        self.tabs.addTab(self._report(), "   Report   ")
        root.addWidget(self.tabs)

    def _header(self):
        f = QFrame()
        f.setFixedHeight(80)
        f.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1e3a8a, stop:0.5 #2563eb, stop:1 #3b82f6);
                border-bottom: 3px solid #60a5fa;
            }}
        """)
        h = QHBoxLayout(f)
        h.setContentsMargins(32, 0, 32, 0)
        h.setSpacing(16)

        ic = QLabel("⛁")
        ic.setStyleSheet(f"font-size:32px;color:#93c5fd;border:none;background:transparent;")
        h.addWidget(ic)

        t = QLabel("System Monitor")
        t.setStyleSheet(f"color:{WHITE};font-size:24px;font-weight:800;border:none;background:transparent;")
        h.addWidget(t)

        s = QLabel("│")
        s.setStyleSheet(f"color:#60a5fa;font-size:20px;border:none;background:transparent;")
        h.addWidget(s)

        sub = QLabel("Crash Logger & Diagnostics")
        sub.setStyleSheet(f"color:#bfdbfe;font-size:14px;border:none;background:transparent;")
        h.addWidget(sub)

        h.addStretch()

        self._dot = QLabel("●")
        self._dot.setStyleSheet(f"color:#f87171;font-size:16px;border:none;background:transparent;")
        h.addWidget(self._dot)

        self._stxt = QLabel("Stopped")
        self._stxt.setStyleSheet(f"""
            color:{DANGER};font-size:13px;font-weight:700;
            padding:8px 20px;background:{DANGER_LIGHT};
            border:1px solid #fecaca;border-radius:20px;
        """)
        h.addWidget(self._stxt)

        return f

    # ---- Dashboard ----
    def _dash(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(20)

        sec = QLabel("System Overview")
        sec.setStyleSheet(f"font-size:18px;font-weight:800;color:{GRAY_900};border:none;background:transparent;")
        lay.addWidget(sec)

        # Cards row 1
        row1 = QHBoxLayout()
        row1.setSpacing(16)
        self.c_cpu = Card("CPU USAGE", "—", "of total cores", ACCENT)
        self.c_mem = Card("MEMORY", "—", "of total RAM", PURPLE)
        self.c_swap = Card("SWAP", "—", "of total swap", DANGER)
        self.c_disk = Card("DISK", "—", "of root partition", TEAL)
        row1.addWidget(self.c_cpu)
        row1.addWidget(self.c_mem)
        row1.addWidget(self.c_swap)
        row1.addWidget(self.c_disk)
        lay.addLayout(row1)

        # Cards row 2
        row2 = QHBoxLayout()
        row2.setSpacing(16)
        self.c_temp = Card("TEMPERATURE", "—", "CPU thermal zone", ORANGE)
        self.c_uptime = Card("UPTIME", "—", "since last boot", SUCCESS)
        self.c_caps = Card("CAPTURES", "—", "total cycles", "#6366f1")
        self.c_logsz = Card("LOG SIZE", "—", "total disk used", "#d97706")
        row2.addWidget(self.c_temp)
        row2.addWidget(self.c_uptime)
        row2.addWidget(self.c_caps)
        row2.addWidget(self.c_logsz)
        lay.addLayout(row2)

        # Bars
        bg = QGroupBox("Resource Utilization")
        bl = QVBoxLayout(bg)
        bl.setSpacing(12)
        self.b_cpu = Bar("CPU", ACCENT)
        self.b_mem = Bar("Memory", PURPLE)
        self.b_swap = Bar("Swap", DANGER)
        self.b_disk = Bar("Disk", TEAL)
        bl.addWidget(self.b_cpu)
        bl.addWidget(self.b_mem)
        bl.addWidget(self.b_swap)
        bl.addWidget(self.b_disk)
        lay.addWidget(bg)

        # Activity
        ag = QGroupBox("Recent System Activity")
        al = QVBoxLayout(ag)
        self.act = QTextEdit()
        self.act.setReadOnly(True)
        self.act.setMaximumHeight(170)
        self.act.setLineWrapMode(QTextEdit.NoWrap)
        al.addWidget(self.act)
        lay.addWidget(ag)

        return w

    # ---- Controls ----
    def _ctrls(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(20)

        g1 = QGroupBox("Monitor Controls")
        g1l = QHBoxLayout(g1)
        g1l.setSpacing(16)

        self.btn_start = QPushButton("Start Monitoring")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setMinimumHeight(52)
        self.btn_start.clicked.connect(self._start)
        g1l.addWidget(self.btn_start)

        self.btn_stop = QPushButton("Stop Monitoring")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.setMinimumHeight(52)
        self.btn_stop.clicked.connect(self._stop)
        g1l.addWidget(self.btn_stop)

        rb = QPushButton("Refresh Status")
        rb.setObjectName("btnSecondary")
        rb.setMinimumHeight(52)
        rb.clicked.connect(self._check_status)
        g1l.addWidget(rb)

        lay.addWidget(g1)

        # Config
        g2 = QGroupBox("Configuration")
        g2l = QGridLayout(g2)
        g2l.setSpacing(12)
        g2l.setColumnStretch(1, 1)

        info = [
            ("Script Path", str(SCRIPT_PATH)),
            ("Log Directory", str(LOG_DIR)),
            ("Capture Interval", "Every 5 seconds"),
            ("Max Log Size", "500 MB per file (auto-rotated)"),
            ("Rotated Files", "10 per category"),
        ]
        for i, (k, v) in enumerate(info):
            lk = QLabel(k)
            lk.setStyleSheet(f"font-weight:700;color:{GRAY_600};border:none;background:transparent;")
            lv = QLabel(v)
            lv.setStyleSheet(f"color:{GRAY_800};border:none;background:transparent;")
            lv.setTextInteractionFlags(Qt.TextSelectableByMouse)
            g2l.addWidget(lk, i, 0)
            g2l.addWidget(lv, i, 1)

        lay.addWidget(g2)

        # Overview table
        g3 = QGroupBox("Log Files Overview")
        g3l = QVBoxLayout(g3)

        self.otbl = QTableWidget()
        self.otbl.setColumnCount(4)
        self.otbl.setHorizontalHeaderLabels(["Category", "Files", "Total Size", "Latest File"])
        self.otbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.otbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.otbl.setSelectionBehavior(QTableWidget.SelectRows)
        self.otbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self.otbl.verticalHeader().setVisible(False)
        self.otbl.doubleClicked.connect(self._open_tab)
        g3l.addWidget(self.otbl)

        ob = QPushButton("Refresh Overview")
        ob.setObjectName("btnSecondary")
        ob.clicked.connect(self._refresh_ov)
        g3l.addWidget(ob)

        lay.addWidget(g3)
        lay.addStretch()
        return w

    # ---- Report ----
    def _report(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        top = QHBoxLayout()
        gb = QPushButton("Generate Report")
        gb.setObjectName("btnAccent")
        gb.setMinimumHeight(50)
        gb.clicked.connect(self._gen_report)
        top.addWidget(gb)
        eb = QPushButton("Export Report")
        eb.setObjectName("btnSecondary")
        eb.setMinimumHeight(50)
        eb.clicked.connect(self._exp_report)
        top.addWidget(eb)
        top.addStretch()
        lay.addLayout(top)

        self.rpt = QTextEdit()
        self.rpt.setReadOnly(True)
        self.rpt.setLineWrapMode(QTextEdit.NoWrap)
        lay.addWidget(self.rpt)
        return w

    # ---- Menu ----
    def _menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("File")
        ea = QAction("Export All Logs…", self); ea.setShortcut("Ctrl+E"); ea.triggered.connect(self._exp_all); fm.addAction(ea)
        fm.addSeparator()
        qa = QAction("Quit", self); qa.setShortcut("Ctrl+Q"); qa.triggered.connect(self.close); fm.addAction(qa)

        mm = mb.addMenu("Monitor")
        a1 = QAction("Start", self); a1.setShortcut("F5"); a1.triggered.connect(self._start); mm.addAction(a1)
        a2 = QAction("Stop", self); a2.setShortcut("Shift+F5"); a2.triggered.connect(self._stop); mm.addAction(a2)
        mm.addSeparator()
        a3 = QAction("Status", self); a3.setShortcut("F6"); a3.triggered.connect(self._check_status); mm.addAction(a3)
        a4 = QAction("Report", self); a4.setShortcut("F7"); a4.triggered.connect(self._gen_report); mm.addAction(a4)

        vm = mb.addMenu("View")
        names = ["Dashboard","Controls","Kernel","System","Hardware","Power","Network","Processes","Snapshots","Report"]
        for i, n in enumerate(names):
            a = QAction(n, self); a.setShortcut(f"Ctrl+{i+1 if i<9 else 0}")
            a.triggered.connect(lambda _, idx=i: self.tabs.setCurrentIndex(idx))
            vm.addAction(a)

        hm = mb.addMenu("Help")
        aa = QAction("About", self); aa.triggered.connect(self._about); hm.addAction(aa)

    # ---- Timers ----
    def _timers(self):
        QTimer(self, interval=REFRESH_MS, timeout=self._refresh_dash).start()
        QTimer(self, interval=5000, timeout=self._check_status).start()

    # ---- Actions ----
    def _start(self):
        if not SCRIPT_PATH.exists():
            return QMessageBox.critical(self, "Error", f"Not found:\n{SCRIPT_PATH}")
        if self._running:
            return QMessageBox.information(self, "Running", "Already running.")
        subprocess.Popen(["bash", str(SCRIPT_PATH)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.statusBar().showMessage("Monitor started")
        QTimer.singleShot(1000, self._check_status)

    def _stop(self):
        if not self._running:
            return QMessageBox.information(self, "Off", "Not running.")
        if QMessageBox.question(self, "Stop", f"Stop monitor (PID {self._pid})?",
                                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            try: os.kill(self._pid, 15)
            except: pass
            QTimer.singleShot(1000, self._check_status)

    def _check_status(self):
        pf = LOG_DIR / ".monitor.pid"
        if pf.exists():
            try:
                pid = int(pf.read_text().strip())
                os.kill(pid, 0)
                self._running, self._pid = True, pid
                return self._set_st(True, pid)
            except: pass
        self._running, self._pid = False, None
        self._set_st(False)

    def _set_st(self, on, pid=None):
        if on:
            self._dot.setStyleSheet(f"color:#4ade80;font-size:16px;border:none;background:transparent;")
            self._stxt.setText(f"Running  PID {pid}")
            self._stxt.setStyleSheet(f"color:{SUCCESS};font-size:13px;font-weight:700;padding:8px 20px;background:{SUCCESS_LIGHT};border:1px solid #bbf7d0;border-radius:20px;")
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
        else:
            self._dot.setStyleSheet(f"color:#f87171;font-size:16px;border:none;background:transparent;")
            self._stxt.setText("Stopped")
            self._stxt.setStyleSheet(f"color:{DANGER};font-size:13px;font-weight:700;padding:8px 20px;background:{DANGER_LIGHT};border:1px solid #fecaca;border-radius:20px;")
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)

    def _refresh_dash(self):
        cmd = ("bash -c '"
               "echo CPU:$(top -bn1|grep \"Cpu(s)\"|awk \"{print \\$2}\");"
               "echo MEM:$(free|awk \"/Mem:/ {printf \\\"%.1f\\\",\\$3/\\$2*100}\");"
               "echo SWAP:$(free|awk \"/Swap:/ {if(\\$2>0)printf \\\"%.1f\\\",\\$3/\\$2*100;else print 0}\");"
               "echo DISK:$(df /|awk \"NR==2{print \\$5}\");"
               "echo UPTIME:$(uptime -p);"
               "echo TEMP:$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null|awk \"{printf \\\"%.0f\\\",\\$1/1000}\")'")
        w = Worker(cmd, 10)
        w.done.connect(self._on_dash)
        w.start()
        self._w = w

    def _on_dash(self, out):
        d = {}
        for l in out.split('\n'):
            if ':' in l:
                k, _, v = l.partition(':'); d[k.strip()] = v.strip()

        def pct(s):
            try: return float(d[s].replace('%','').strip())
            except: return 0

        if 'CPU' in d:
            v = pct('CPU')
            self.c_cpu.set(f"{v:.0f}%", "of total cores"); self.b_cpu.set(v)
        if 'MEM' in d:
            v = pct('MEM')
            self.c_mem.set(f"{v:.0f}%", "of total RAM"); self.b_mem.set(v)
        if 'SWAP' in d:
            v = pct('SWAP')
            self.c_swap.set(f"{v:.0f}%", "of total swap"); self.b_swap.set(v)
        if 'DISK' in d:
            v = pct('DISK')
            self.c_disk.set(f"{v:.0f}%", "of root partition"); self.b_disk.set(v)
        if 'UPTIME' in d:
            self.c_uptime.set(d['UPTIME'].replace('up','').strip())
        if 'TEMP' in d:
            t = d['TEMP'].strip()
            self.c_temp.set(f"{t}°C" if t and t!='0' else "N/A", "CPU thermal zone")

        cl = LOG_DIR / ".capture_log"
        if cl.exists():
            try: self.c_caps.set(str(len(cl.read_text().strip().split('\n'))), "total cycles")
            except: pass

        ts = self._dsz(LOG_DIR)
        if ts > 1024**3: self.c_logsz.set(f"{ts/1024**3:.1f} GB", "total disk used")
        elif ts > 1024**2: self.c_logsz.set(f"{ts/1024**2:.1f} MB", "total disk used")
        else: self.c_logsz.set(f"{ts/1024:.1f} KB", "total disk used")

        jf = LOG_DIR/"system"/f"journal_{datetime.now().strftime('%Y%m%d')}.log"
        if jf.exists():
            try:
                ls = jf.read_text(errors='replace').strip().split('\n')
                dl = [l for l in ls if not l.startswith('=====') and l.strip()]
                self.act.setPlainText('\n'.join(dl[-30:]))
                c = self.act.textCursor(); c.movePosition(QTextCursor.End); self.act.setTextCursor(c)
            except: pass

    def _refresh_ov(self):
        cats = ["kernel","system","hardware","power","network","processes","snapshots"]
        self.otbl.setRowCount(len(cats))
        for i, cat in enumerate(cats):
            d = LOG_DIR/cat
            if d.exists():
                fs = list(d.glob("*.log"))
                ts = sum(f.stat().st_size for f in fs)
                lt = max(fs, key=lambda f: f.stat().st_mtime).name if fs else "—"
                ss = f"{ts/1024**2:.1f} MB" if ts>1024**2 else (f"{ts/1024:.1f} KB" if ts>1024 else f"{ts} B")
            else: fs, ss, lt = [], "0 B", "—"
            for c, v, a in [(0,cat.upper(),Qt.AlignLeft),(1,str(len(fs)),Qt.AlignCenter),(2,ss,Qt.AlignRight|Qt.AlignVCenter),(3,lt,Qt.AlignLeft)]:
                it = QTableWidgetItem(v); it.setTextAlignment(a)
                if c==0: it.setFont(QFont("Ubuntu",10,QFont.Bold))
                self.otbl.setItem(i, c, it)

    def _open_tab(self, idx):
        cat = self.otbl.item(idx.row(), 0).text().lower()
        m = {"kernel":2,"system":3,"hardware":4,"power":5,"network":6,"processes":7,"snapshots":8}
        if cat in m:
            self.tabs.setCurrentIndex(m[cat])
            v = self.tabs.widget(m[cat])
            if hasattr(v, 'refresh'): v.refresh()

    def _gen_report(self):
        self.tabs.setCurrentIndex(9)
        self.rpt.setPlainText("Generating…")
        w = Worker(f"bash -c '{SCRIPT_PATH} --report'", 30)
        w.done.connect(lambda o: self.rpt.setPlainText(o))
        w.err.connect(lambda e: self.rpt.setPlainText(f"Error: {e}"))
        w.start(); self._rw = w

    def _exp_report(self):
        p, _ = QFileDialog.getSaveFileName(self, "Export", f"report_{datetime.now():%Y%m%d_%H%M%S}.txt", "Text (*.txt)")
        if p:
            try:
                r = subprocess.run(["bash",str(SCRIPT_PATH),"--report"], capture_output=True, text=True, timeout=30)
                open(p,'w').write(r.stdout+r.stderr)
                self.statusBar().showMessage(f"Exported: {p}")
            except Exception as e: QMessageBox.warning(self, "Error", str(e))

    def _exp_all(self):
        d = QFileDialog.getExistingDirectory(self, "Export To")
        if d:
            try:
                import shutil
                dp = Path(d)/f"logs_{datetime.now():%Y%m%d_%H%M%S}"
                shutil.copytree(LOG_DIR, dp)
                QMessageBox.information(self, "Done", f"Exported to:\n{dp}")
            except Exception as e: QMessageBox.warning(self, "Error", str(e))

    def _about(self):
        QMessageBox.about(self, "About System Monitor",
            "<h2>System Monitor — Crash Logger & Diagnostics</h2>"
            "<p>Professional real-time system monitoring for Linux.</p>"
            "<p>Logs CPU, memory, disk, temperature, power events, and kernel messages "
            "to diagnose random shutdowns and freezes.</p>"
            "<hr>"
            "<p style='color:#6b7280;'>Developed with love by <b>Vishal Ravi</b><br>"
            "<i>System Admin</i></p>")

    @staticmethod
    def _dsz(p):
        t=0
        try:
            for dp,_,fs in os.walk(p):
                for f in fs: t+=os.path.getsize(os.path.join(dp,f))
        except: pass
        return t

    def closeEvent(self, e):
        if self._running:
            r = QMessageBox.question(self, "Quit", "Stop monitor and quit?",
                                     QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if r == QMessageBox.Cancel: e.ignore(); return
            if r == QMessageBox.Yes:
                try: os.kill(self._pid, 15)
                except: pass
        e.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setFont(QFont("Ubuntu", 10))
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
