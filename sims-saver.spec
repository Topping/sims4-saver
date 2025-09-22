# -*- mode: python ; coding: utf-8 -*-

import platform
import os

a = Analysis(
    [os.path.join('sims_saver', 'main.py')],
    pathex=[],
    binaries=[],
    datas=[('sims_saver/localization.py', 'sims_saver/'),
           ('icon.ico', '.'),
           ('icon.png', '.'),
           ('icon.icns', '.'),
           ],
    hiddenimports=['pystray'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe_name = 'Sims4-Save-Helper'
exe_icon = 'icon.ico'

if platform.system() == "Darwin": # macOS
    exe_name = 'Sims4-Save-Helper'
    exe_icon = 'icon.icns'
elif platform.system() == "Windows": # Windows
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
)

app = BUNDLE(
    exe,
    name='Sims4-Save-Helper.app',
    icon='icon.icns',
    bundle_identifier=None,
    info_plist={
        'CFBundleName': 'Sims4-Save-Helper',
        'CFBundleDisplayName': 'Sims4-Save-Helper',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Topping 2025',
    },
 )
