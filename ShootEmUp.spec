# -*- mode: python ; coding: utf-8 -*-

import os
import glob
import moderngl

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# ---------- ModernGL ----------
moderngl_path = os.path.dirname(moderngl.__file__)
mgl_files = glob.glob(os.path.join(moderngl_path, "mgl*.pyd"))

if not mgl_files:
    raise RuntimeError("mgl binary not found!")

binaries = [
    (mgl_files[0], "moderngl"),
]

# ---------- Imports ----------
hiddenimports = (
    collect_submodules("game_engine") +
    collect_submodules("classes") +
    collect_submodules("constants") +
    collect_submodules("states") +
    [
        "glcontext",
        "glcontext.wgl",
    ]
)

# ---------- Analysis ----------
a = Analysis(
    ["Game.py"],
    pathex=["."],
    binaries=binaries,
    datas=[],  
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)


exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ShootEmUp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="ShootEmUp",
)