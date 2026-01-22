# -*- mode: python ; coding: utf-8 -*-

import platform
import os
from pathlib import Path

# Version from environment or default
VERSION = os.environ.get('VERSION', 'dev')

block_cipher = None

# Collect QML files
qml_files = []
qml_dir = Path('sims_saver/qml')
if qml_dir.exists():
    for qml_file in qml_dir.rglob('*'):
        if qml_file.is_file():
            rel_path = qml_file.relative_to('sims_saver/qml')
            qml_files.append((str(qml_file), str(Path('sims_saver/qml') / rel_path.parent)))

# Data files
datas = [
    ('icon.ico', '.'),
    ('icon.png', '.'),
    ('icon.icns', '.'),
]
datas.extend(qml_files)

# Hidden imports for PySide6 and Qt Quick
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtQml',
    'PySide6.QtQuick',
    'PySide6.QtQuickControls2',
    'sims_saver.app_controller',
    'sims_saver.settings_manager',
    'sims_saver.autosave_service',
    'sims_saver.keyboard_service',
    'sims_saver.process_detector',
    'sims_saver.localization',
]

a = Analysis(
    [os.path.join('sims_saver', 'main.py')],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'PIL',
        'pystray',
        # Unused Qt modules - excluding these significantly reduces binary size
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DExtras',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DRender',
        'PySide6.QtBluetooth',
        'PySide6.QtCharts',
        'PySide6.QtConcurrent',
        'PySide6.QtDataVisualization',
        'PySide6.QtDesigner',
        'PySide6.QtHelp',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtNetwork',
        'PySide6.QtNetworkAuth',
        'PySide6.QtNfc',
        'PySide6.QtOpenGL',
        'PySide6.QtOpenGLWidgets',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'PySide6.QtPositioning',
        'PySide6.QtPrintSupport',
        'PySide6.QtRemoteObjects',
        'PySide6.QtScxml',
        'PySide6.QtSensors',
        'PySide6.QtSerialBus',
        'PySide6.QtSerialPort',
        'PySide6.QtSpatialAudio',
        'PySide6.QtSql',
        'PySide6.QtStateMachine',
        'PySide6.QtSvg',
        'PySide6.QtSvgWidgets',
        'PySide6.QtTest',
        'PySide6.QtTextToSpeech',
        'PySide6.QtUiTools',
        'PySide6.QtWebChannel',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineQuick',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebSockets',
        'PySide6.QtWidgets',
        'PySide6.QtXml',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe_name = 'Sims4-Save-Helper'
exe_icon = 'icon.ico'

if platform.system() == "Darwin":  # macOS
    exe_name = 'Sims4-Save-Helper'
    exe_icon = 'icon.icns'
elif platform.system() == "Windows":
    exe_name = 'Sims4-Save-Helper'
    exe_icon = 'icon.ico'

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=exe_name,
    icon=exe_icon,
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS app bundle
if platform.system() == "Darwin":
    app = BUNDLE(
        exe,
        name='Sims4-Save-Helper.app',
        icon='icon.icns',
        bundle_identifier='com.topping.sims4savehelper',
        info_plist={
            'CFBundleName': 'Sims4-Save-Helper',
            'CFBundleDisplayName': 'The Sims 4 Save Helper',
            'CFBundleVersion': VERSION,
            'CFBundleShortVersionString': VERSION,
            'NSHumanReadableCopyright': 'Topping 2025',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.14.0',
        },
    )
