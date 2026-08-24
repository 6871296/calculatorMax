# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for CalculatorMax.

Usage:
    pyinstaller calculatormax.spec --distpath dist --workpath build
"""

from PyInstaller.building.build_main import Analysis, PYZ, EXE, BUNDLE
import sys
import os


# Repository root
repo_root = os.path.abspath(os.path.dirname(SPECPATH))


# Collect hidden imports that may be loaded dynamically at runtime.
hiddenimports = [
    'simpleeval',
    'six',
    'pyperclip',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    # maliang and its submodules
    'maliang',
    'maliang.color',
    'maliang.core',
    'maliang.core.configs',
    'maliang.core.containers',
    'maliang.core.virtual',
    'maliang.theme',
    'maliang.toolbox',
    # sympy subpackages are usually picked up by PyInstaller hooks,
    # but keep the top-level package explicit to be safe.
    'sympy',
    'sympy.core',
    'sympy.solvers',
    'sympy.polys',
    'sympy.functions',
    # forex-python may be used in the (currently disabled) money converter.
    'forex_python',
    'forex_python.converter',
]


a = Analysis(
    ['main.py'],
    pathex=[repo_root],
    binaries=[],
    # Bundle the assets directory so it can be resolved at runtime.
    datas=[('assets', 'assets')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='calculatormax',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windowed GUI application
    windowed=True,
)
