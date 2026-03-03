#!/usr/bin/env python3
# ============================================================
#  houdini_shelf.py  —  AOV Manager · Houdini Shelf Tool
#
#  INSTALL:
#  1. In Houdini, right-click the shelf → New Tool
#  2. Go to the Script tab
#  3. Paste the entire contents of this file
#  4. Set the icon and label as you like (e.g. label: "AOV Mgr")
#  5. Click Accept
#
#  IMPORTANT:
#  aov_config.py must be somewhere Python can find it.
#  Easiest options:
#    a) Put aov_config.py in $HOUDINI_USER_PREF_DIR/scripts/python/
#    b) Put aov_config.py next to this file and add its folder
#       to $PYTHONPATH in houdini.env
#
#  This tool reads ALL configuration from aov_config.py.
#  To add passes or presets, edit aov_config.py only.
# ============================================================

import hou
import os
import sys

# ── Locate aov_config ───────────────────────────────────────
# Try common locations
_config_search = [
    os.path.join(hou.expandString("$HOUDINI_USER_PREF_DIR"), "scripts", "python"),
    os.path.join(hou.expandString("$HIP")),
    os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else "",
]
for _p in _config_search:
    if _p and os.path.exists(os.path.join(_p, "aov_config.py")):
        if _p not in sys.path:
            sys.path.insert(0, _p)
        break

try:
    import aov_config as cfg
except ImportError:
    hou.ui.displayMessage(
        "AOV Manager: Cannot find aov_config.py.\n\n"
        "Place aov_config.py in one of:\n"
        "  $HOUDINI_USER_PREF_DIR/scripts/python/\n"
        "  $HIP (your hip file directory)\n\n"
        "Then re-run the shelf tool.",
        severity=hou.severityType.Error
    )
    raise

# ── PySide2 (Houdini's built-in Qt) ─────────────────────────
from PySide2.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QCheckBox,
    QComboBox, QScrollArea, QFrame, QTextEdit, QTabWidget,
    QGroupBox, QSplitter, QSizePolicy, QApplication, QMessageBox
)
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFont, QColor

# ── Theme (matches standalone_app.py) ───────────────────────
BG_DARK  = "#0a0c10"
BG_MID   = "#111520"
BG_PANEL = "#161b26"
BG_CARD  = "#1a2030"
BORDER   = "#2a3040"
TEXT_PRI = "#e8eaf0"
TEXT_SEC = "#6a7a90"
TEXT_DIM = "#3a4a5a"

PRESET_COLORS = {
    "ocean":     "#00d4ff",
    "scifi":     "#bf5fff",
    "painterly": "#ffb347",
}

MONO_FONT = "JetBrains Mono, Consolas, Courier New"
UI_FONT   = "Segoe UI, Helvetica Neue, Arial"


def _stylesheet(accent):
    return f"""
    QDialog, QWidget {{
        background-color: {BG_DARK};
        color: {TEXT_PRI};
        font-family: {UI_FONT};
        font-size: 12px;
    }}
    QLineEdit, QSpinBox, QComboBox {{
        background-color: {BG_PANEL};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 5px 8px;
        color: {TEXT_PRI};
        font-family: {MONO_FONT};
        font-size: 11px;
    }}
    QLineEdit:focus, QSpinBox:focus {{ border: 1px solid {accent}; }}
    QPushButton {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 6px 14px;
        color: {TEXT_PRI};
        font-size: 11px;
    }}
    QPushButton:hover {{ border: 1px solid {accent}; color: {accent}; }}
    QPushButton#primary {{
        background-color: {accent}22;
        border: 1px solid {accent};
        color: {accent};
        font-weight: bold;
        padding: 9px 18px;
    }}
    QPushButton#primary:hover {{ background-color: {accent}44; }}
    QPushButton#build_btn {{
        background-color: {"#22aa6622"};
        border: 1px solid {"#22aa66"};
        color: {"#22aa66"};
        font-weight: bold;
        font-size: 13px;
        padding: 10px 18px;
    }}
    QPushButton#build_btn:hover {{ background-color: {"#22aa6644"}; }}
    QCheckBox {{ color: {TEXT_PRI}; spacing: 6px; }}
    QCheckBox::indicator {{
        width: 13px; height: 13px;
        border-radius: 3px;
        border: 1px solid {BORDER};
        background-color: {BG_PANEL};
    }}
    QCheckBox::indicator:checked {{
        background-color: {accent};
        border: 1px solid {accent};
    }}
    QTabBar::tab {{
        background: transparent; color: {TEXT_SEC};
        padding: 7px 14px;
        border: none;
        border-bottom: 2px solid transparent;
        font-size: 10px; font-weight: bold; letter-spacing: 1px;
    }}
    QTabBar::tab:selected {{ color: {accent}; border-bottom: 2px solid {accent}; }}
    QTabWidget::pane {{
        border: 1px solid {BORDER}; border-radius: 5px;
        background-color: {BG_PANEL};
    }}
    QTextEdit {{
        background-color: #050810;
        border: 1px solid {BORDER};
        border-radius: 5px;
        color: #aaffcc;
        font-family: {MONO_FONT};
        font-size: 11px;
        padding: 6px;
    }}
    QGroupBox {{
        color: {accent};
        border: 1px solid {BORDER};
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 6px;
        font-size: 9px;
        font-weight: bold;
        letter-spacing: 1px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
    }}
    QScrollBar:vertical {{
        background: {BG_DARK}; width: 5px; border-radius: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER}; border-radius: 2px; min-height: 16px;
    }}
    QFrame#card_on {{
        background-color: {accent}30;
        border: 1px solid {accent};
        border-radius: 6px;
    }}
    QFrame#card_off {{
        background-color: transparent;
        border: 1px solid {BORDER};
        border-radius: 6px;
    }}
    """


# ── Pass Card (same pattern as standalone) ───────────────────
class PassCard(QFrame):
    toggled = Signal(str, bool)

    def __init__(self, pass_id, label, desc, default_on=True, accent="#00d4ff", parent=None):
        super().__init__(parent)
        self.pass_id = pass_id
        self.accent  = accent
        self._active = default_on
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(6)

        self.dot = QLabel("●")
        self.dot.setFixedWidth(12)

        col = QVBoxLayout()
        col.setSpacing(0)
        self.lbl = QLabel(label.upper())
        self.lbl.setFont(QFont(UI_FONT, 10, QFont.Bold))
        self.dsc = QLabel(desc)
        self.dsc.setFont(QFont(MONO_FONT, 8))
        col.addWidget(self.lbl)
        col.addWidget(self.dsc)

        lay.addWidget(self.dot)
        lay.addLayout(col)
        lay.addStretch()

        self._refresh()

    def _refresh(self):
        if self._active:
            self.setObjectName("card_on")
            bg = self.accent + "28"
            self.setStyleSheet(
                "QFrame#card_on {{ background-color: {bg}; "
                "border: 1px solid {acc}; border-radius: 6px; }}".format(
                    bg=bg, acc=self.accent)
            )
            self.dot.setStyleSheet("color: {}; font-size: 9px;".format(self.accent))
            self.lbl.setStyleSheet("color: #ffffff; font-size: 10px; font-weight: 700;")
            self.dsc.setStyleSheet("color: #c0ccd8; font-size: 8px;")
        else:
            self.setObjectName("card_off")
            self.setStyleSheet(
                "QFrame#card_off {{ background-color: transparent; "
                "border: 1px solid {b}; border-radius: 6px; }}".format(b=BORDER)
            )
            self.dot.setStyleSheet("color: #2a3a4a; font-size: 9px;")
            self.lbl.setStyleSheet("color: #4a5a6a; font-size: 10px; font-weight: 600;")
            self.dsc.setStyleSheet("color: #3a4a5a; font-size: 8px;")
        self.setStyle(self.style())

    def mousePressEvent(self, event):
        self._active = not self._active
        self._refresh()
        self.toggled.emit(self.pass_id, self._active)

    @property
    def is_active(self):
        return self._active


# ── Main Dialog ──────────────────────────────────────────────
class AOVManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent or hou.qt.mainWindow())
        self.setWindowTitle("AOV Manager  ·  Houdini")
        self.resize(980, 700)
        self.setMinimumSize(800, 560)

        self.current_preset   = cfg.DEFAULT_PRESET
        self.current_pipeline = cfg.DEFAULT_PIPELINE
        self.film_mode        = False
        self.standard_cards   = {}
        self.custom_cards     = {}

        self._build_ui()
        self._populate_passes()
        self.setStyleSheet(_stylesheet(PRESET_COLORS[self.current_preset]))

    # ── UI ───────────────────────────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # Content split
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.addWidget(self._build_config_panel())
        splitter.addWidget(self._build_output_panel())
        splitter.setSizes([560, 420])
        root.addWidget(splitter, 1)

    def _build_sidebar(self):
        w = QWidget()
        w.setFixedWidth(185)
        w.setStyleSheet(f"background-color: {BG_MID}; border-right: 1px solid {BORDER};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(14, 20, 14, 14)
        lay.setSpacing(5)

        t = QLabel("AOV")
        t.setFont(QFont(UI_FONT, 20, QFont.Bold))
        t.setStyleSheet(f"color: {PRESET_COLORS[self.current_preset]};")
        s = QLabel("MANAGER  ·  HOUDINI")
        s.setFont(QFont(UI_FONT, 8))
        s.setStyleSheet(f"color: {TEXT_SEC}; letter-spacing: 2px;")
        lay.addWidget(t)
        lay.addWidget(s)
        lay.addSpacing(14)

        # Pipeline
        lay.addWidget(self._slbl("Pipeline"))
        self.pipe_btns = []
        for i, pipe in enumerate(cfg.PIPELINES):
            btn = QPushButton(pipe)
            btn.setCheckable(True)
            btn.setChecked(i == self.current_pipeline)
            btn.clicked.connect(lambda _, idx=i: self._set_pipeline(idx))
            lay.addWidget(btn)
            self.pipe_btns.append(btn)

        lay.addSpacing(14)
        lay.addWidget(self._slbl("Style Preset"))
        self.preset_btns = {}
        for key, data in cfg.PRESETS.items():
            btn = QPushButton(data["label"])
            btn.setCheckable(True)
            btn.setChecked(key == self.current_preset)
            btn.clicked.connect(lambda _, k=key: self._set_preset(k))
            lay.addWidget(btn)
            self.preset_btns[key] = btn

        lay.addSpacing(14)
        lay.addWidget(self._slbl("Mode"))
        self.film_cb = QCheckBox("  Film Mode (ACES)")
        self.film_cb.toggled.connect(lambda v: setattr(self, "film_mode", v))
        lay.addWidget(self.film_cb)

        lay.addStretch()

        note = QLabel("Shelf tool\naov_config.py drives\nall settings.")
        note.setFont(QFont(UI_FONT, 8))
        note.setStyleSheet(f"color: {TEXT_DIM}; line-height: 1.5;")
        lay.addWidget(note)
        return w

    def _slbl(self, text):
        l = QLabel(text.upper())
        accent = PRESET_COLORS[self.current_preset]
        l.setStyleSheet(f"color: {accent}; letter-spacing: 2px; font-size: 8px; font-weight: bold;")
        return l

    def _build_config_panel(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 10, 16)
        lay.setSpacing(10)

        # Project fields
        gb = QGroupBox("PROJECT")
        gl = QGridLayout(gb)
        gl.setSpacing(6)

        gl.addWidget(QLabel("Project"), 0, 0)
        self.proj_edit = QLineEdit(cfg.DEFAULT_PROJECT)
        self.proj_edit.textChanged.connect(self._update_preview)
        gl.addWidget(self.proj_edit, 0, 1)

        gl.addWidget(QLabel("Layer"), 1, 0)
        self.layer_edit = QLineEdit(cfg.DEFAULT_LAYER)
        self.layer_edit.textChanged.connect(self._update_preview)
        gl.addWidget(self.layer_edit, 1, 1)

        gl.addWidget(QLabel("Version"), 2, 0)
        self.ver_spin = QSpinBox()
        self.ver_spin.setMinimum(1)
        self.ver_spin.setMaximum(999)
        self.ver_spin.setValue(cfg.DEFAULT_VERSION)
        self.ver_spin.valueChanged.connect(self._update_preview)
        gl.addWidget(self.ver_spin, 2, 1)

        gl.addWidget(QLabel("Root Path"), 3, 0)
        self.root_edit = QLineEdit(cfg.DEFAULT_ROOT)
        self.root_edit.textChanged.connect(self._update_preview)
        gl.addWidget(self.root_edit, 3, 1)

        lay.addWidget(gb)

        # Tabs
        self.tabs = QTabWidget()

        # Passes tab
        ptab = QWidget()
        pl = QVBoxLayout(ptab)
        pl.setContentsMargins(6, 6, 6, 6)
        pl.setSpacing(6)

        pl.addWidget(self._slbl("Standard Passes"))
        std_scroll = QScrollArea()
        std_scroll.setWidgetResizable(True)
        std_scroll.setFixedHeight(180)
        std_inner = QWidget()
        self.std_grid = QGridLayout(std_inner)
        self.std_grid.setSpacing(4)
        std_scroll.setWidget(std_inner)
        pl.addWidget(std_scroll)

        self.cust_preset_lbl = self._slbl("Preset Passes")
        pl.addWidget(self.cust_preset_lbl)
        cust_scroll = QScrollArea()
        cust_scroll.setWidgetResizable(True)
        cust_scroll.setFixedHeight(130)
        cust_inner = QWidget()
        self.cust_grid = QGridLayout(cust_inner)
        self.cust_grid.setSpacing(4)
        cust_scroll.setWidget(cust_inner)
        pl.addWidget(cust_scroll)

        self.count_lbl = QLabel()
        self.count_lbl.setFont(QFont(MONO_FONT, 9))
        self.count_lbl.setStyleSheet(f"color: {TEXT_SEC};")
        pl.addWidget(self.count_lbl)

        self.tabs.addTab(ptab, "AOV PASSES")

        # Naming tab
        ntab = QWidget()
        nl = QVBoxLayout(ntab)
        nl.setContentsMargins(6, 6, 6, 6)
        nl.setSpacing(6)

        nl.addWidget(QLabel("Template:"))
        self.naming_edit = QLineEdit()
        self.naming_edit.textChanged.connect(self._update_preview)
        nl.addWidget(self.naming_edit)

        nl.addWidget(QLabel("Preview:"))
        self.preview_lbl = QLabel()
        self.preview_lbl.setFont(QFont(MONO_FONT, 9))
        self.preview_lbl.setStyleSheet(f"color: {TEXT_SEC}; background: {BG_PANEL}; border: 1px solid {BORDER}; border-radius: 4px; padding: 5px 8px;")
        self.preview_lbl.setWordWrap(True)
        nl.addWidget(self.preview_lbl)

        nl.addWidget(QLabel("Tokens:"))
        tr = QHBoxLayout()
        for tok in ["{project}", "{layer}", "{pass}", "{version}", "{date}", "{frame}"]:
            b = QPushButton(tok)
            b.setFont(QFont(MONO_FONT, 8))
            b.setFixedHeight(24)
            b.clicked.connect(lambda _, t=tok: self.naming_edit.setText(self.naming_edit.text() + t))
            tr.addWidget(b)
        nl.addLayout(tr)
        nl.addStretch()

        self.tabs.addTab(ntab, "NAMING")
        lay.addWidget(self.tabs, 1)
        return w

    def _build_output_panel(self):
        w = QWidget()
        w.setStyleSheet(f"background-color: {BG_MID};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(10, 16, 16, 16)
        lay.setSpacing(8)

        hdr = QHBoxLayout()
        out_l = QLabel("EXPORT SCRIPT")
        out_l.setStyleSheet(f"color: {TEXT_SEC}; letter-spacing: 2px; font-size: 9px; font-weight: bold;")
        hdr.addWidget(out_l)
        hdr.addStretch()

        cp_btn = QPushButton("⊞ Copy")
        cp_btn.setObjectName("primary")
        cp_btn.setFixedHeight(26)
        cp_btn.clicked.connect(self._copy)
        hdr.addWidget(cp_btn)
        lay.addLayout(hdr)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText(
            "Click 'Generate Script' to preview,\nor 'Build in Houdini' to create nodes directly."
        )
        lay.addWidget(self.output_edit, 1)

        # Two action buttons
        self.gen_btn = QPushButton("✦  Generate Script")
        self.gen_btn.setObjectName("primary")
        self.gen_btn.setFixedHeight(38)
        self.gen_btn.clicked.connect(self._generate_script)

        self.build_btn = QPushButton("⬡  Build in Houdini")
        self.build_btn.setObjectName("build_btn")
        self.build_btn.setFixedHeight(38)
        self.build_btn.clicked.connect(self._build_in_houdini)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.addWidget(self.gen_btn)
        btn_row.addWidget(self.build_btn)
        lay.addLayout(btn_row)

        return w

    # ── Pass population ──────────────────────────────────────
    def _populate_passes(self):
        accent = PRESET_COLORS[self.current_preset]

        for grid in (self.std_grid, self.cust_grid):
            for i in reversed(range(grid.count())):
                w = grid.itemAt(i).widget()
                if w:
                    w.deleteLater()
        self.standard_cards.clear()
        self.custom_cards.clear()

        for idx, p in enumerate(cfg.STANDARD_PASSES):
            card = PassCard(p["id"], p["label"], p["desc"], p["default_on"], accent)
            card.toggled.connect(self._on_toggled)
            self.std_grid.addWidget(card, idx // 2, idx % 2)
            self.standard_cards[p["id"]] = card

        for idx, p in enumerate(cfg.PRESETS[self.current_preset]["passes"]):
            card = PassCard(p["id"], p["label"], p["desc"], p["default_on"], accent)
            card.toggled.connect(self._on_toggled)
            self.cust_grid.addWidget(card, idx // 2, idx % 2)
            self.custom_cards[p["id"]] = card

        self.naming_edit.setText(cfg.PRESETS[self.current_preset]["naming_template"])
        self._update_count()
        self._update_preview()

    def _on_toggled(self, pid, active):
        self._update_count()

    def _update_count(self):
        s = sum(1 for c in self.standard_cards.values() if c.is_active)
        p = sum(1 for c in self.custom_cards.values()   if c.is_active)
        self.count_lbl.setText(f"  Total: {s+p} active  ·  Standard: {s}  ·  Preset: {p}")

    def _update_preview(self):
        t = self.naming_edit.text()
        prev = cfg.resolve_name(t,
            self.proj_edit.text()  or "project",
            self.layer_edit.text() or "layer",
            "beauty", self.ver_spin.value(), self.current_pipeline)
        self.preview_lbl.setText(prev + ".$F4.exr")

    # ── Interactions ─────────────────────────────────────────
    def _set_pipeline(self, idx):
        self.current_pipeline = idx
        accent = PRESET_COLORS[self.current_preset]
        for i, btn in enumerate(self.pipe_btns):
            active = i == idx
            btn.setStyleSheet(f"""
                QPushButton {{ background: {accent+'22' if active else 'transparent'};
                               border: 1px solid {accent if active else BORDER};
                               border-radius: 4px; padding: 6px 10px;
                               color: {accent if active else TEXT_SEC};
                               font-size: 11px; text-align: left; }}
                QPushButton:hover {{ border-color: {accent}66; }}
            """)
        self._update_preview()

    def _set_preset(self, key):
        self.current_preset = key
        accent = PRESET_COLORS[key]
        for k, btn in self.preset_btns.items():
            col = PRESET_COLORS[k]
            active = k == key
            btn.setStyleSheet(f"""
                QPushButton {{ background: {col+'22' if active else 'transparent'};
                               border: 1px solid {col if active else BORDER};
                               border-radius: 4px; padding: 6px 10px;
                               color: {col if active else TEXT_SEC};
                               font-size: 11px; text-align: left; }}
                QPushButton:hover {{ border-color: {col}66; }}
            """)
        self.setStyleSheet(_stylesheet(accent))
        self._populate_passes()

    # ── Core actions ─────────────────────────────────────────
    def _get_states(self):
        std  = {pid: c.is_active for pid, c in self.standard_cards.items()}
        cust = {pid: c.is_active for pid, c in self.custom_cards.items()}
        return std, cust

    def _generate_script(self):
        project = self.proj_edit.text()  or "MY_PROJECT"
        layer   = self.layer_edit.text() or "hero_layer"
        version = self.ver_spin.value()
        root    = self.root_edit.text()  or "/renders"
        std, cust = self._get_states()

        if self.current_pipeline < 2:
            text = cfg.generate_houdini_script(
                self.current_pipeline, self.current_preset,
                project, layer, version, root, self.film_mode, std, cust
            )
        else:
            text = cfg.generate_ue5_config(
                self.current_preset, project, layer, version, root,
                self.film_mode, std, cust
            )
        self.output_edit.setPlainText(text)

    def _build_in_houdini(self):
        """Directly execute the generated script inside the running Houdini session."""
        if self.current_pipeline >= 2:
            hou.ui.displayMessage(
                "Build in Houdini is only available for Houdini pipelines.\n"
                "Use Generate Script for UE5 config.",
                severity=hou.severityType.Warning
            )
            return

        project = self.proj_edit.text()  or "MY_PROJECT"
        layer   = self.layer_edit.text() or "hero_layer"
        version = self.ver_spin.value()
        root    = self.root_edit.text()  or "/renders"
        std, cust = self._get_states()

        script = cfg.generate_houdini_script(
            self.current_pipeline, self.current_preset,
            project, layer, version, root, self.film_mode, std, cust
        )
        self.output_edit.setPlainText(script)

        # Execute directly in Houdini's Python context
        try:
            exec(script, {"hou": hou, "__builtins__": __builtins__})
            active_passes = cfg.build_active_passes(
                self.current_preset, std, cust
            )
            renderer = "Mantra" if self.current_pipeline == 0 else "Karma"
            hou.ui.displayMessage(
                f"✦ AOV Manager\n\n"
                f"Successfully built {renderer} ROP:\n"
                f"  Node: /out/{layer}_{'mantra' if self.current_pipeline==0 else 'karma'}_rop\n"
                f"  Passes: {len(active_passes)} active\n"
                f"  Output folders created.",
                title="AOV Manager — Build Complete"
            )
        except Exception as e:
            hou.ui.displayMessage(
                f"Build failed:\n{str(e)}\n\n"
                f"Check the generated script in the output panel.",
                severity=hou.severityType.Error
            )

    def _copy(self):
        text = self.output_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)


# ── Entry point  (called by the shelf button) ────────────────
def run():
    dialog = AOVManagerDialog()
    dialog.show()
    # Keep a reference so it doesn't get garbage-collected
    hou.session.aov_manager_dialog = dialog


run()