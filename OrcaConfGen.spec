# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the OrcaSlicer Profile Generator GUI.

Builds a single-file, windowed (no console) executable that bundles:
  - gui.py / generate.py (code)
  - gui_schema.json       (UI definition)
  - brian_*_gcode.json    (custom gcode assets, read at generation time)

The bundled JSON assets are placed at the bundle root ('.') so generate.py's
_bundle_root() finds them. Writable state (config.json, backups/) is written
next to the executable by _app_dir(), not into the bundle.

Build on each platform:   pyinstaller --noconfirm OrcaConfGen.spec
Output:                    dist/OrcaConfGen[.exe]   (dist/OrcaConfGen.app on macOS)
"""

import glob
import sys

block_cipher = None

# Read-only assets bundled at the root of the unpacked bundle.
datas = [(f, '.') for f in sorted(glob.glob('brian_*_gcode.json'))]
datas.append(('gui_schema.json', '.'))

icon = None  # drop an .ico/.icns path here when branding is ready

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OrcaConfGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)

# macOS: wrap the executable in a .app bundle.
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='OrcaConfGen.app',
        icon=icon,
        bundle_identifier='xyz.hanson.orcaconfgen',
    )
