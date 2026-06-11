"""
OrcaSlicer Profile Generator - GUI
==================================

A thin, schema-driven desktop front-end for generate.py. Every control shown
here is described declaratively in gui_schema.json - this file contains no
hard-coded list of printers, filaments, or options. To expose a new toggle or
field, edit gui_schema.json; no change to this file is required.

The GUI collects the user's selections, calls generate.run_generation() in a
background thread, and streams its console output into a log pane. Selections
are persisted to config.json so the plain `python generate.py` CLI honours the
same configuration.

Run from source:   python gui.py
Frozen (bundled):  OrcaConfGen.exe
"""

import json
import sys

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPlainTextEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

import generate


# --------------------------------------------------------------------------- #
# Schema / config persistence
# --------------------------------------------------------------------------- #

def load_schema() -> dict:
    """Load the declarative UI definition from the bundle/source directory."""
    path = generate._bundle_root() / "gui_schema.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> dict:
    """Load persisted user selections (config.json), or {} if none exists."""
    path = generate._CONFIG_FILE
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(cfg: dict) -> None:
    """Persist user selections so the CLI honours the same configuration."""
    with open(generate._CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
        f.write("\n")


# --------------------------------------------------------------------------- #
# Generation worker
# --------------------------------------------------------------------------- #

class _StreamToSignal:
    """File-like object that forwards writes to a Qt signal (the log pane)."""

    def __init__(self, emit):
        self._emit = emit

    def write(self, text):
        if text:
            self._emit(text)

    def flush(self):
        pass


class GenerationWorker(QThread):
    """Runs generate.run_generation() off the UI thread, streaming stdout."""

    output = Signal(str)
    done = Signal(dict)
    failed = Signal(str)

    def __init__(self, kwargs: dict):
        super().__init__()
        self._kwargs = kwargs

    def run(self):
        old_stdout = sys.stdout
        sys.stdout = _StreamToSignal(self.output.emit)
        try:
            result = generate.run_generation(**self._kwargs)
            self.done.emit(result)
        except Exception as e:  # surface any failure in the log + a dialog
            self.output.emit(f"\nERROR: {e}\n")
            self.failed.emit(str(e))
        finally:
            sys.stdout = old_stdout


# --------------------------------------------------------------------------- #
# Main window
# --------------------------------------------------------------------------- #

class MainWindow(QMainWindow):
    def __init__(self, schema: dict, config: dict):
        super().__init__()
        self.schema = schema
        self.config = config
        self.worker = None

        # Widget registries, populated as the schema is rendered.
        self.toggle_widgets = {}   # config_key -> {option_key: QCheckBox}
        self.field_widgets = {}    # field_key -> control widget
        self.field_rows = {}       # field_key -> row container (for visibility)
        self.field_defs = {}       # field_key -> field schema dict

        app_meta = schema.get("app", {})
        self.setWindowTitle(app_meta.get("title", "Profile Generator"))
        self.resize(820, 760)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header(app_meta))
        root.addWidget(self._build_body(), stretch=1)
        root.addWidget(self._build_footer())

        self._apply_visibility()

    # -- header ------------------------------------------------------------ #

    def _build_header(self, app_meta: dict) -> QWidget:
        header = QWidget()
        header.setObjectName("header")
        lay = QVBoxLayout(header)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(2)

        title = QLabel(app_meta.get("title", "Profile Generator"))
        tf = QFont()
        tf.setPointSize(15)
        tf.setBold(True)
        title.setFont(tf)
        lay.addWidget(title)

        subtitle = app_meta.get("subtitle", "")
        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet("color: #555;")
            lay.addWidget(sub)
        return header

    # -- body (scrollable schema-driven form) ------------------------------ #

    def _build_body(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(16)

        for group in self.schema.get("groups", []):
            lay.addWidget(self._build_group(group))
        lay.addStretch(1)

        scroll.setWidget(container)
        return scroll

    def _build_group(self, group: dict) -> QWidget:
        box = QGroupBox(group.get("title", ""))
        outer = QVBoxLayout(box)
        outer.setSpacing(10)

        help_text = group.get("help")
        if help_text:
            lbl = QLabel(help_text)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #555;")
            outer.addWidget(lbl)

        gtype = group.get("type")
        if gtype == "toggles":
            outer.addLayout(self._build_toggles(group))
        elif gtype == "fields":
            for field in group.get("fields", []):
                outer.addWidget(self._build_field(field))
        return box

    def _build_toggles(self, group: dict):
        config_key = group["config_key"]
        saved = self.config.get(config_key, {})
        columns = max(1, int(group.get("columns", 1)))
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(8)

        self.toggle_widgets.setdefault(config_key, {})
        for i, opt in enumerate(group.get("options", [])):
            key = opt["key"]
            cb = QCheckBox(opt.get("label", key))
            if opt.get("help"):
                cb.setToolTip(opt["help"])
            # Saved value wins; otherwise fall back to the schema default.
            cb.setChecked(bool(saved.get(key, opt.get("default", False))))
            self.toggle_widgets[config_key][key] = cb

            cell = QWidget()
            cell_lay = QVBoxLayout(cell)
            cell_lay.setContentsMargins(0, 0, 0, 0)
            cell_lay.setSpacing(0)
            cell_lay.addWidget(cb)
            if opt.get("help"):
                hint = QLabel(opt["help"])
                hint.setStyleSheet("color: #888; font-size: 11px;")
                hint.setWordWrap(True)
                cell_lay.addWidget(hint)

            grid.addWidget(cell, i // columns, i % columns)
        return grid

    def _build_field(self, field: dict) -> QWidget:
        key = field["key"]
        self.field_defs[key] = field
        row = QWidget()
        lay = QVBoxLayout(row)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)

        ftype = field.get("type")

        if ftype == "bool":
            cb = QCheckBox(field.get("label", key))
            cb.setChecked(bool(field.get("default", False)))
            if field.get("help"):
                cb.setToolTip(field["help"])
            self.field_widgets[key] = cb
            lay.addWidget(cb)
        else:
            label = QLabel(field.get("label", key))
            label.setStyleSheet("font-weight: 600;")
            lay.addWidget(label)

            if ftype == "choice":
                combo = QComboBox()
                for choice in field.get("choices", []):
                    combo.addItem(choice["label"], choice["value"])
                default = field.get("default")
                idx = combo.findData(default)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                combo.currentIndexChanged.connect(self._apply_visibility)
                self.field_widgets[key] = combo
                lay.addWidget(combo)
            elif ftype == "directory":
                hb = QHBoxLayout()
                edit = QLineEdit(str(field.get("default", "")))
                edit.setPlaceholderText("Select a folder…")
                browse = QPushButton("Browse…")
                browse.clicked.connect(lambda _, e=edit: self._browse_dir(e))
                hb.addWidget(edit, stretch=1)
                hb.addWidget(browse)
                self.field_widgets[key] = edit
                lay.addLayout(hb)
            elif ftype == "string":
                edit = QLineEdit(str(field.get("default", "")))
                self.field_widgets[key] = edit
                lay.addWidget(edit)

        if field.get("help") and ftype != "bool":
            hint = QLabel(field["help"])
            hint.setStyleSheet("color: #888; font-size: 11px;")
            hint.setWordWrap(True)
            lay.addWidget(hint)

        self.field_rows[key] = row
        return row

    def _browse_dir(self, edit: QLineEdit):
        start = edit.text() or str(generate._app_dir())
        chosen = QFileDialog.getExistingDirectory(self, "Choose output folder", start)
        if chosen:
            edit.setText(chosen)

    # -- footer (log + actions) -------------------------------------------- #

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        lay = QVBoxLayout(footer)
        lay.setContentsMargins(20, 0, 20, 16)
        lay.setSpacing(8)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(200)
        mono = QFont("Consolas")
        mono.setStyleHint(QFont.Monospace)
        mono.setPointSize(9)
        self.log.setFont(mono)
        self.log.setPlaceholderText("Generation output will appear here…")
        lay.addWidget(self.log)

        btn_row = QHBoxLayout()
        self.status = QLabel("Ready.")
        self.status.setStyleSheet("color: #555;")
        btn_row.addWidget(self.status, stretch=1)

        self.save_btn = QPushButton("Save Config")
        self.save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(self.save_btn)

        self.generate_btn = QPushButton("Generate Profiles")
        self.generate_btn.setDefault(True)
        self.generate_btn.setMinimumWidth(160)
        self.generate_btn.clicked.connect(self._on_generate)
        btn_row.addWidget(self.generate_btn)

        lay.addLayout(btn_row)
        return footer

    # -- visibility (visible_when) ----------------------------------------- #

    def _apply_visibility(self):
        for key, field in self.field_defs.items():
            cond = field.get("visible_when")
            row = self.field_rows.get(key)
            if not cond or row is None:
                continue
            ctrl = self.field_widgets.get(cond.get("field"))
            current = ctrl.currentData() if isinstance(ctrl, QComboBox) else None
            row.setVisible(current == cond.get("equals"))

    # -- collection -------------------------------------------------------- #

    def _collect_toggles(self, config_key: str) -> dict:
        return {k: cb.isChecked() for k, cb in self.toggle_widgets.get(config_key, {}).items()}

    def _field_value(self, key: str):
        w = self.field_widgets.get(key)
        if isinstance(w, QCheckBox):
            return w.isChecked()
        if isinstance(w, QComboBox):
            return w.currentData()
        if isinstance(w, QLineEdit):
            return w.text().strip()
        return None

    def _current_config(self) -> dict:
        return {
            "ENABLED_PRINTERS": self._collect_toggles("ENABLED_PRINTERS"),
            "OPTIONAL_FILAMENTS": self._collect_toggles("OPTIONAL_FILAMENTS"),
        }

    # -- actions ----------------------------------------------------------- #

    def _on_save(self):
        try:
            save_config(self._current_config())
            self.status.setText(f"Saved config to {generate._CONFIG_FILE}")
        except OSError as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def _on_generate(self):
        if self.worker and self.worker.isRunning():
            return

        output_mode = self._field_value("output_mode")
        output_dir = self._field_value("output_dir") if output_mode == "custom" else None
        do_clean = bool(self._field_value("do_clean"))
        dry_run = bool(self._field_value("dry_run"))

        # Validate
        if not any(self._collect_toggles("ENABLED_PRINTERS").values()):
            QMessageBox.warning(self, "No printers selected",
                                "Enable at least one printer before generating.")
            return
        if output_mode == "custom" and not output_dir:
            QMessageBox.warning(self, "No output folder",
                                "Choose a custom output folder, or switch to "
                                "'OrcaSlicer config'.")
            return

        # Confirm destructive clean of the live OrcaSlicer config
        if do_clean and not dry_run and output_dir is None:
            resp = QMessageBox.warning(
                self, "Clean existing profiles?",
                "This will DELETE all previously generated profiles in your "
                "OrcaSlicer config before writing new ones.\n\nA timestamped "
                "backup is taken first. Continue?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if resp != QMessageBox.Yes:
                return

        # Persist selections so the CLI stays in sync.
        try:
            save_config(self._current_config())
        except OSError:
            pass  # non-fatal; generation can still proceed

        kwargs = dict(
            enabled_printers=self._collect_toggles("ENABLED_PRINTERS"),
            optional_filaments=self._collect_toggles("OPTIONAL_FILAMENTS"),
            output_dir=output_dir,
            dry_run=dry_run,
            do_clean=do_clean,
        )

        self.log.clear()
        self.generate_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.status.setText("Generating…")

        self.worker = GenerationWorker(kwargs)
        self.worker.output.connect(self._append_log)
        self.worker.done.connect(self._on_done)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _append_log(self, text: str):
        self.log.moveCursor(QTextCursor.End)
        self.log.insertPlainText(text)
        self.log.moveCursor(QTextCursor.End)

    def _on_done(self, result: dict):
        if result.get("backup_only"):
            self.status.setText("Backup complete.")
            return
        total = result.get("total", 0)
        fil = result.get("filament", 0)
        self.status.setText(f"Done — {total} profiles + {fil} filament updates.")

    def _on_failed(self, message: str):
        self.status.setText("Failed.")
        QMessageBox.critical(self, "Generation failed", message)

    def _on_worker_finished(self):
        self.generate_btn.setEnabled(True)
        self.save_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OrcaSlicer Profile Generator")
    schema = load_schema()
    config = load_config()
    win = MainWindow(schema, config)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
