#!/usr/bin/env python3
# ============================================================
#  standalone_app.py  —  AOV Manager · Standalone PySide6 App
#
#  Requirements:  pip install PySide6
#  Run:           python standalone_app.py
#                 Or double-click if your OS has Python associated
#
#  This app shares all configuration with aov_config.py.
#  To add/remove passes or presets, edit aov_config.py only.
# ============================================================

import sys
import os
import datetime

# ── Allow running from any directory ────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aov_config as cfg

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox,
    QCheckBox, QScrollArea, QFrame, QTextEdit, QTabWidget,
    QGroupBox, QSpinBox, QSplitter, QMessageBox, QFileDialog,
    QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

# ── Theme ────────────────────────────────────────────────────
BG_DARK   = "#0a0c10"
BG_MID    = "#111520"
BG_PANEL  = "#161b26"
BG_CARD   = "#1a2030"
BORDER    = "#2a3040"
TEXT_PRI  = "#e8eaf0"
TEXT_SEC  = "#6a7a90"
TEXT_DIM  = "#3a4a5a"
ACCENT    = "#00d4ff"   # default; overridden per preset

PRESET_COLORS = {
    "ocean":     "#00d4ff",
    "scifi":     "#bf5fff",
    "painterly": "#ffb347",
}

MONO_FONT  = "JetBrains Mono, Consolas, Courier New, monospace"
UI_FONT    = "Segoe UI, SF Pro Display, Helvetica Neue, sans-serif"


def make_stylesheet(accent=ACCENT):
    return f"""
    QMainWindow, QWidget {{
        background-color: {BG_DARK};
        color: {TEXT_PRI};
        font-family: {UI_FONT};
        font-size: 13px;
    }}
    QLabel {{
        color: {TEXT_PRI};
    }}
    QLabel#section_label {{
        color: {accent};
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}
    QLineEdit, QSpinBox, QComboBox {{
        background-color: {BG_PANEL};
        border: 1px solid {BORDER};
        border-radius: 5px;
        padding: 6px 10px;
        color: {TEXT_PRI};
        font-family: {MONO_FONT};
        font-size: 12px;
        selection-background-color: {accent};
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {accent};
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {BG_PANEL};
        border: 1px solid {BORDER};
        selection-background-color: {accent}44;
        color: {TEXT_PRI};
    }}
    QPushButton {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 5px;
        padding: 7px 16px;
        color: {TEXT_PRI};
        font-size: 12px;
    }}
    QPushButton:hover {{
        border: 1px solid {accent};
        color: {accent};
    }}
    QPushButton#primary_btn {{
        background-color: {accent}22;
        border: 1px solid {accent};
        color: {accent};
        font-weight: 600;
        font-size: 13px;
        padding: 10px 20px;
        border-radius: 6px;
    }}
    QPushButton#primary_btn:hover {{
        background-color: {accent}44;
    }}
    QPushButton#copy_btn {{
        background-color: {BG_CARD};
        border: 1px solid {accent}66;
        color: {accent};
        font-size: 11px;
        padding: 5px 12px;
    }}
    QCheckBox {{
        color: {TEXT_PRI};
        spacing: 8px;
        font-size: 12px;
    }}
    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
        border-radius: 3px;
        border: 1px solid {BORDER};
        background-color: {BG_PANEL};
    }}
    QCheckBox::indicator:checked {{
        background-color: {accent};
        border: 1px solid {accent};
    }}
    QCheckBox::indicator:hover {{
        border: 1px solid {accent};
    }}
    QTabWidget::pane {{
        border: 1px solid {BORDER};
        border-radius: 6px;
        background-color: {BG_PANEL};
    }}
    QTabBar::tab {{
        background-color: transparent;
        color: {TEXT_SEC};
        padding: 8px 18px;
        border: none;
        border-bottom: 2px solid transparent;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
    }}
    QTabBar::tab:selected {{
        color: {accent};
        border-bottom: 2px solid {accent};
    }}
    QTabBar::tab:hover {{
        color: {TEXT_PRI};
    }}
    QTextEdit {{
        background-color: #050810;
        border: 1px solid {BORDER};
        border-radius: 6px;
        color: #aaffcc;
        font-family: {MONO_FONT};
        font-size: 12px;
        padding: 8px;
        selection-background-color: {accent}44;
    }}
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollBar:vertical {{
        background: {BG_DARK};
        width: 6px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 3px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {accent}88;
    }}
    QFrame#card {{
        background-color: transparent;
        border: 1px solid {BORDER};
        border-radius: 7px;
    }}
    QFrame#card_active {{
        background-color: transparent;
        border: 1px solid {accent};
        border-radius: 7px;
    }}
    QGroupBox {{
        color: {TEXT_SEC};
        border: 1px solid {BORDER};
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 8px;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 1px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 6px;
        color: {accent};
    }}
    QSplitter::handle {{
        background-color: {BORDER};
        width: 1px;
    }}
    """


# ── Pass Card Widget ─────────────────────────────────────────
class PassCard(QFrame):
    toggled = Signal(str, bool)

    def __init__(self, pass_id, label, desc, default_on=True, accent=ACCENT, parent=None):
        super().__init__(parent)
        self.pass_id  = pass_id
        self.label    = label
        self.desc     = desc
        self.accent   = accent
        self._active  = default_on
        self.setFixedHeight(56)
        self.setCursor(Qt.PointingHandCursor)
        self._build()
        self._refresh()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        self.dot = QLabel("●")
        self.dot.setFixedWidth(14)
        self.dot.setFont(QFont("Arial", 8))

        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        self.lbl = QLabel(self.label.upper())
        self.lbl.setFont(QFont(UI_FONT, 11, QFont.Bold))
        self.dsc = QLabel(self.desc)
        self.dsc.setFont(QFont(MONO_FONT, 9))
        text_col.addWidget(self.lbl)
        text_col.addWidget(self.dsc)

        layout.addWidget(self.dot)
        layout.addLayout(text_col)
        layout.addStretch()

    def _refresh(self):
        if self._active:
            acc = self.accent
            bg  = acc + "18"
            self.setStyleSheet(
                "QFrame { background-color: " + bg + "; "
                "border: 1px solid " + acc + "; border-radius: 7px; }"
            )
            self.dot.setStyleSheet("color: " + acc + "; font-size: 10px;")
            self.lbl.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: 700;")
            self.dsc.setStyleSheet("color: #c0ccd8; font-size: 9px;")
        else:
            self.setStyleSheet(
                "QFrame { background-color: transparent; "
                "border: 1px solid " + BORDER + "; border-radius: 7px; }"
            )
            self.dot.setStyleSheet("color: #2a3a4a; font-size: 10px;")
            self.lbl.setStyleSheet("color: #4a5a6a; font-size: 11px; font-weight: 600;")
            self.dsc.setStyleSheet("color: #3a4a5a; font-size: 9px;")

    def mousePressEvent(self, event):
        self._active = not self._active
        self._refresh()
        self.toggled.emit(self.pass_id, self._active)

    def set_active(self, val):
        self._active = val
        self._refresh()

    @property
    def is_active(self):
        return self._active


# ── Main Window ──────────────────────────────────────────────
class AOVManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AOV Manager")
        self.resize(1100, 780)
        self.setMinimumSize(900, 600)

        # State
        self.current_preset   = cfg.DEFAULT_PRESET
        self.current_pipeline = cfg.DEFAULT_PIPELINE
        self.film_mode        = False
        self.standard_cards   = {}   # pass_id → PassCard
        self.custom_cards     = {}   # pass_id → PassCard

        self._build_ui()
        self._apply_theme()
        self._populate_passes()

    # ── UI Construction ─────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # Main content
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([620, 480])

        root.addWidget(splitter, 1)

    def _section_label(self, text):
        lbl = QLabel(text.upper())
        lbl.setObjectName("section_label")
        lbl.setFont(QFont(UI_FONT, 9, QFont.Bold))
        lbl.setStyleSheet(f"color: {PRESET_COLORS[self.current_preset]}; letter-spacing: 2px; font-size: 9px; font-weight: 700;")
        return lbl

    def _build_sidebar(self):
        w = QWidget()
        w.setFixedWidth(200)
        w.setStyleSheet(f"background-color: {BG_MID}; border-right: 1px solid {BORDER};")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(6)

        # Title
        title = QLabel("AOV")
        title.setFont(QFont(UI_FONT, 22, QFont.Bold))
        title.setStyleSheet(f"color: {ACCENT}; letter-spacing: 2px;")
        sub = QLabel("MANAGER")
        sub.setFont(QFont(UI_FONT, 9))
        sub.setStyleSheet(f"color: {TEXT_SEC}; letter-spacing: 4px; margin-top: -6px;")
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(20)

        # Pipeline
        layout.addWidget(self._section_label("Pipeline"))
        layout.addSpacing(4)
        self.pipeline_btns = []
        for i, pipe in enumerate(cfg.PIPELINES):
            btn = QPushButton(pipe)
            btn.setCheckable(True)
            btn.setChecked(i == self.current_pipeline)
            btn.clicked.connect(lambda checked, idx=i: self._set_pipeline(idx))
            btn.setStyleSheet(f"""
                QPushButton {{ background: {'#00d4ff18' if i == self.current_pipeline else 'transparent'};
                               border: 1px solid {'#00d4ff' if i == self.current_pipeline else BORDER};
                               border-radius: 5px; padding: 7px 10px;
                               color: {'#00d4ff' if i == self.current_pipeline else TEXT_SEC};
                               font-size: 11px; text-align: left; }}
                QPushButton:hover {{ border-color: #00d4ff66; color: {TEXT_PRI}; }}
            """)
            layout.addWidget(btn)
            self.pipeline_btns.append(btn)

        layout.addSpacing(20)

        # Presets
        layout.addWidget(self._section_label("Style Preset"))
        layout.addSpacing(4)
        self.preset_btns = {}
        for key, data in cfg.PRESETS.items():
            col = PRESET_COLORS[key]
            btn = QPushButton(data["label"])
            btn.setCheckable(True)
            btn.setChecked(key == self.current_preset)
            btn.clicked.connect(lambda checked, k=key: self._set_preset(k))
            active = key == self.current_preset
            btn.setStyleSheet(f"""
                QPushButton {{ background: {col + '22' if active else 'transparent'};
                               border: 1px solid {col if active else BORDER};
                               border-radius: 5px; padding: 7px 10px;
                               color: {col if active else TEXT_SEC};
                               font-size: 11px; text-align: left; }}
                QPushButton:hover {{ border-color: {col}66; }}
            """)
            layout.addWidget(btn)
            self.preset_btns[key] = btn

        layout.addSpacing(20)

        # Film mode toggle
        layout.addWidget(self._section_label("Mode"))
        layout.addSpacing(4)
        self.film_cb = QCheckBox("  Film Mode (ACES)")
        self.film_cb.setChecked(False)
        self.film_cb.toggled.connect(self._on_film_toggle)
        layout.addWidget(self.film_cb)

        layout.addStretch()

        # Version info
        ver = QLabel("AOV Manager v1.0\nEdit aov_config.py to\ncustomise passes & presets.")
        ver.setFont(QFont(UI_FONT, 9))
        ver.setStyleSheet(f"color: {TEXT_DIM}; line-height: 1.6;")
        layout.addWidget(ver)
        return w

    def _build_left_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 12, 20)
        layout.setSpacing(14)

        # Project fields
        fields_box = QGroupBox("PROJECT")
        fl = QGridLayout(fields_box)
        fl.setSpacing(8)

        fl.addWidget(QLabel("Project Name"), 0, 0)
        self.proj_edit = QLineEdit(cfg.DEFAULT_PROJECT)
        self.proj_edit.textChanged.connect(self._update_preview)
        fl.addWidget(self.proj_edit, 0, 1)

        fl.addWidget(QLabel("Layer Name"), 1, 0)
        self.layer_edit = QLineEdit(cfg.DEFAULT_LAYER)
        self.layer_edit.textChanged.connect(self._update_preview)
        fl.addWidget(self.layer_edit, 1, 1)

        fl.addWidget(QLabel("Version"), 2, 0)
        self.ver_spin = QSpinBox()
        self.ver_spin.setMinimum(1)
        self.ver_spin.setMaximum(999)
        self.ver_spin.setValue(cfg.DEFAULT_VERSION)
        self.ver_spin.valueChanged.connect(self._update_preview)
        fl.addWidget(self.ver_spin, 2, 1)

        fl.addWidget(QLabel("Root Path"), 3, 0)
        self.root_edit = QLineEdit(cfg.DEFAULT_ROOT)
        self.root_edit.textChanged.connect(self._update_preview)
        fl.addWidget(self.root_edit, 3, 1)

        layout.addWidget(fields_box)

        # Tabs: Passes | Naming
        self.tabs = QTabWidget()

        # ── Passes tab
        passes_w = QWidget()
        passes_l = QVBoxLayout(passes_w)
        passes_l.setContentsMargins(8, 8, 8, 8)
        passes_l.setSpacing(8)

        # Standard passes
        std_lbl = QLabel("STANDARD PASSES")
        std_lbl.setFont(QFont(UI_FONT, 9, QFont.Bold))
        std_lbl.setStyleSheet(f"color: {TEXT_SEC}; letter-spacing: 2px;")
        passes_l.addWidget(std_lbl)

        self.std_scroll = QScrollArea()
        self.std_scroll.setWidgetResizable(True)
        self.std_scroll.setFixedHeight(200)
        std_inner = QWidget()
        self.std_grid = QGridLayout(std_inner)
        self.std_grid.setSpacing(5)
        self.std_scroll.setWidget(std_inner)
        passes_l.addWidget(self.std_scroll)

        # Custom passes
        self.custom_lbl = QLabel("PRESET PASSES")
        self.custom_lbl.setFont(QFont(UI_FONT, 9, QFont.Bold))
        self.custom_lbl.setStyleSheet(f"color: {PRESET_COLORS[self.current_preset]}; letter-spacing: 2px;")
        passes_l.addWidget(self.custom_lbl)

        self.cust_scroll = QScrollArea()
        self.cust_scroll.setWidgetResizable(True)
        self.cust_scroll.setFixedHeight(150)
        cust_inner = QWidget()
        self.cust_grid = QGridLayout(cust_inner)
        self.cust_grid.setSpacing(5)
        self.cust_scroll.setWidget(cust_inner)
        passes_l.addWidget(self.cust_scroll)

        # Pass count bar
        self.pass_count_lbl = QLabel()
        self.pass_count_lbl.setFont(QFont(MONO_FONT, 10))
        self.pass_count_lbl.setStyleSheet(f"color: {TEXT_SEC}; padding: 4px 0;")
        passes_l.addWidget(self.pass_count_lbl)

        self.tabs.addTab(passes_w, "AOV PASSES")

        # ── Naming tab
        naming_w = QWidget()
        naming_l = QVBoxLayout(naming_w)
        naming_l.setContentsMargins(8, 8, 8, 8)
        naming_l.setSpacing(8)

        naming_l.addWidget(QLabel("Naming Template:"))
        self.naming_edit = QLineEdit()
        self.naming_edit.textChanged.connect(self._update_preview)
        naming_l.addWidget(self.naming_edit)

        naming_l.addWidget(QLabel("Live Preview:"))
        self.naming_preview = QLabel()
        self.naming_preview.setFont(QFont(MONO_FONT, 10))
        self.naming_preview.setStyleSheet(f"color: {TEXT_SEC}; background: {BG_PANEL}; border: 1px solid {BORDER}; border-radius: 4px; padding: 6px 10px;")
        self.naming_preview.setWordWrap(True)
        naming_l.addWidget(self.naming_preview)

        naming_l.addWidget(QLabel("Click token to append:"))
        tok_row = QHBoxLayout()
        for tok in ["{project}", "{layer}", "{pass}", "{version}", "{date}", "{frame}"]:
            b = QPushButton(tok)
            b.setFont(QFont(MONO_FONT, 9))
            b.setFixedHeight(28)
            b.clicked.connect(lambda _, t=tok: self.naming_edit.setText(self.naming_edit.text() + t))
            tok_row.addWidget(b)
        naming_l.addLayout(tok_row)
        naming_l.addStretch()

        self.tabs.addTab(naming_w, "NAMING")

        layout.addWidget(self.tabs, 1)

        return w

    def _build_right_panel(self):
        w = QWidget()
        w.setStyleSheet(f"background-color: {BG_MID};")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 20, 20, 20)
        layout.setSpacing(10)

        # Header row
        hdr = QHBoxLayout()
        out_lbl = QLabel("EXPORT OUTPUT")
        out_lbl.setFont(QFont(UI_FONT, 9, QFont.Bold))
        out_lbl.setStyleSheet(f"color: {TEXT_SEC}; letter-spacing: 2px;")
        hdr.addWidget(out_lbl)
        hdr.addStretch()

        self.copy_btn = QPushButton("⊞  Copy")
        self.copy_btn.setObjectName("copy_btn")
        self.copy_btn.setFixedHeight(28)
        self.copy_btn.clicked.connect(self._copy_output)
        hdr.addWidget(self.copy_btn)

        self.save_btn = QPushButton("↓  Save")
        self.save_btn.setObjectName("copy_btn")
        self.save_btn.setFixedHeight(28)
        self.save_btn.clicked.connect(self._save_output)
        hdr.addWidget(self.save_btn)

        layout.addLayout(hdr)

        # Output text area
        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText(
            "Configure your settings on the left,\nthen click Generate to produce the export script."
        )
        layout.addWidget(self.output_edit, 1)

        # Generate button
        self.gen_btn = QPushButton("✦  Generate Config")
        self.gen_btn.setObjectName("primary_btn")
        self.gen_btn.setFixedHeight(44)
        self.gen_btn.clicked.connect(self._generate)
        layout.addWidget(self.gen_btn)

        return w

    # ── Pass population ─────────────────────────────────────
    def _populate_passes(self):
        accent = PRESET_COLORS[self.current_preset]

        # Clear existing
        for i in reversed(range(self.std_grid.count())):
            w = self.std_grid.itemAt(i).widget()
            if w:
                w.deleteLater()
        for i in reversed(range(self.cust_grid.count())):
            w = self.cust_grid.itemAt(i).widget()
            if w:
                w.deleteLater()
        self.standard_cards.clear()
        self.custom_cards.clear()

        # Standard passes — 2 columns
        for idx, p in enumerate(cfg.STANDARD_PASSES):
            card = PassCard(p["id"], p["label"], p["desc"], p["default_on"], accent)
            card.toggled.connect(self._on_pass_toggled)
            self.std_grid.addWidget(card, idx // 2, idx % 2)
            self.standard_cards[p["id"]] = card

        # Custom passes
        for idx, p in enumerate(cfg.PRESETS[self.current_preset]["passes"]):
            card = PassCard(p["id"], p["label"], p["desc"], p["default_on"], accent)
            card.toggled.connect(self._on_pass_toggled)
            self.cust_grid.addWidget(card, idx // 2, idx % 2)
            self.custom_cards[p["id"]] = card

        # Update naming template
        self.naming_edit.setText(cfg.PRESETS[self.current_preset]["naming_template"])

        # Update label color
        self.custom_lbl.setStyleSheet(f"color: {accent}; letter-spacing: 2px;")
        self.custom_lbl.setText(f"{cfg.PRESETS[self.current_preset]['label']} — CUSTOM PASSES")

        self._update_pass_count()
        self._update_preview()

    def _on_pass_toggled(self, pass_id, active):
        self._update_pass_count()
        self._update_preview()

    def _update_pass_count(self):
        std_count  = sum(1 for c in self.standard_cards.values() if c.is_active)
        cust_count = sum(1 for c in self.custom_cards.values()   if c.is_active)
        accent = PRESET_COLORS[self.current_preset]
        self.pass_count_lbl.setText(
            f"  Total: {std_count + cust_count} active  ·  "
            f"Standard: {std_count}  ·  Preset: {cust_count}"
        )

    # ── Preview ─────────────────────────────────────────────
    def _update_preview(self):
        template = self.naming_edit.text()
        project  = self.proj_edit.text()  or "project"
        layer    = self.layer_edit.text() or "layer"
        version  = self.ver_spin.value()
        preview  = cfg.resolve_name(template, project, layer, "beauty", version, self.current_pipeline)
        self.naming_preview.setText(preview + ".$F4.exr")

    # ── Interactions ─────────────────────────────────────────
    def _set_pipeline(self, idx):
        self.current_pipeline = idx
        accent = PRESET_COLORS[self.current_preset]
        for i, btn in enumerate(self.pipeline_btns):
            active = i == idx
            btn.setStyleSheet(f"""
                QPushButton {{ background: {accent + '22' if active else 'transparent'};
                               border: 1px solid {accent if active else BORDER};
                               border-radius: 5px; padding: 7px 10px;
                               color: {accent if active else TEXT_SEC};
                               font-size: 11px; text-align: left; }}
                QPushButton:hover {{ border-color: {accent}66; color: {TEXT_PRI}; }}
            """)
        self._update_preview()
        self._update_gen_btn_label()

    def _set_preset(self, key):
        self.current_preset = key
        accent = PRESET_COLORS[key]
        for k, btn in self.preset_btns.items():
            col = PRESET_COLORS[k]
            active = k == key
            btn.setStyleSheet(f"""
                QPushButton {{ background: {col + '22' if active else 'transparent'};
                               border: 1px solid {col if active else BORDER};
                               border-radius: 5px; padding: 7px 10px;
                               color: {col if active else TEXT_SEC};
                               font-size: 11px; text-align: left; }}
                QPushButton:hover {{ border-color: {col}66; }}
            """)
        # Refresh section labels
        for lbl in self.findChildren(QLabel, "section_label"):
            lbl.setStyleSheet(f"color: {accent}; letter-spacing: 2px; font-size: 9px; font-weight: 700;")
        self._populate_passes()
        self._apply_theme()
        self._update_gen_btn_label()

    def _on_film_toggle(self, state):
        self.film_mode = state

    def _update_gen_btn_label(self):
        pipe = cfg.PIPELINES[self.current_pipeline]
        self.gen_btn.setText(f"✦  Generate {pipe.split('/')[0].strip()} Config")

    def _apply_theme(self):
        accent = PRESET_COLORS[self.current_preset]
        self.setStyleSheet(make_stylesheet(accent))
        self._update_gen_btn_label()

    # ── Generate ─────────────────────────────────────────────
    def _get_states(self):
        std  = {pid: card.is_active for pid, card in self.standard_cards.items()}
        cust = {pid: card.is_active for pid, card in self.custom_cards.items()}
        return std, cust

    def _generate(self):
        project  = self.proj_edit.text()  or "MY_PROJECT"
        layer    = self.layer_edit.text() or "hero_layer"
        version  = self.ver_spin.value()
        root     = self.root_edit.text()  or "/renders"
        std, cust = self._get_states()

        if self.current_pipeline < 2:
            output = cfg.generate_houdini_script(
                self.current_pipeline, self.current_preset,
                project, layer, version, root, self.film_mode, std, cust
            )
        else:
            output = cfg.generate_ue5_config(
                self.current_preset, project, layer, version, root,
                self.film_mode, std, cust
            )

        self.output_edit.setPlainText(output)
        self._last_output = output

    def _copy_output(self):
        text = self.output_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)

    def _save_output(self):
        text = self.output_edit.toPlainText()
        if not text:
            QMessageBox.warning(self, "Nothing to save", "Generate a config first.")
            return
        pipe  = cfg.PIPELINES[self.current_pipeline]
        ext   = ".py" if self.current_pipeline < 2 else ".ini"
        name  = f"aov_{self.proj_edit.text()}_{self.layer_edit.text()}{ext}"
        path, _ = QFileDialog.getSaveFileName(self, "Save Config", name,
                                               "Python (*.py);;INI (*.ini);;All (*)")
        if path:
            with open(path, "w") as f:
                f.write(text)


# ── Entry point ──────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AOV Manager")

    win = AOVManagerApp()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()