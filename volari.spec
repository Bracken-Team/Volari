# -*- mode: python ; coding: utf-8 -*-
# Volari GUI PyInstaller Spec File
# Build command: pyinstaller volari.spec

import os
import sys
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

# Import BUNDLE for macOS (may not exist on other platforms)
try:
    from PyInstaller.building.osx import BUNDLE
except ImportError:
    BUNDLE = None

block_cipher = None

# Get the spec file directory
spec_dir = os.path.dirname(os.path.abspath(SPEC))
sys.path.insert(0, spec_dir)

# Icon path for macOS
icon_path = os.path.join(spec_dir, 'volatility_gui', 'resources', 'Volari.icns')

# Collect dynamic libraries
binaries = []
try:
    import capstone
    binaries += collect_dynamic_libs('capstone')
except ImportError:
    pass

# Collect all necessary data files and hidden imports
volatility_data = (
    collect_data_files('volatility3.framework') +
    collect_data_files('volatility3.framework.automagic', include_py_files=True) +
    collect_data_files('volatility3.framework.plugins', include_py_files=True) +
    collect_data_files('volatility3.framework.layers', include_py_files=True) +
    collect_data_files('volatility3.schemas') +
    collect_data_files('volatility3.plugins', include_py_files=True)
)

# GUI resources
gui_data = [
    (os.path.join(spec_dir, 'volatility_gui', 'resources'), 'volatility_gui/resources'),
]

volatility_imports = (
    collect_submodules('volatility3.framework.automagic') +
    collect_submodules('volatility3.framework.plugins') +
    collect_submodules('volatility3.framework.symbols') +
    collect_submodules('volatility3.framework.layers')
)

# GUI-specific hidden imports
gui_imports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    'matplotlib',
    'matplotlib.backends.backend_qtagg',
    'reportlab',
    'reportlab.lib',
    'reportlab.platypus',
    'vt',
    'requests',
    'json',
    'csv',
    'html',
    'volatility_gui',
    'volatility_gui.ui',
    'volatility_gui.logic',
    # PyObjC for macOS window customization
    'objc',
    'AppKit',
    'Foundation',
    'Cocoa',
]

# Main analysis
a = Analysis(
    ['volatility_gui/main.py'],
    pathex=[spec_dir],
    binaries=binaries,
    datas=volatility_data + gui_data,
    hiddenimports=volatility_imports + gui_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Platform-specific configuration
if sys.platform == 'darwin':
    # macOS: Build as .app bundle
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='Volari',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,  # No console window
        disable_windowed_traceback=False,
        argv_emulation=True,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='Volari',
    )
    
    app = BUNDLE(
        coll,
        name='Volari.app',
        icon=icon_path,  # Use the .icns icon
        bundle_identifier='org.volatility.volari',
        info_plist={
            'CFBundleName': 'Volari',
            'CFBundleDisplayName': 'Volari',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleExecutable': 'Volari',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,  # Support dark mode
            'LSMinimumSystemVersion': '10.13.0',
            'LSApplicationCategoryType': 'public.app-category.utilities',
        },
    )

elif sys.platform == 'win32':
    # Windows: Build as .exe
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='Volari',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # GUI app, no console
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=os.path.join(spec_dir, 'volatility_gui', 'resources', 'volari.ico'),
    )

else:
    # Linux: Build as directory (for AppImage)
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='volari',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='volari',
    )
