# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('data.json', '.'), ('users.json', '.'), ('shared_links.json', '.'), ('components', 'components'), ('utils.py', '.'), ('html_generator.py', '.'), ('data.py', '.'), ('.streamlit', '.streamlit')],
    hiddenimports=['streamlit.runtime.scriptrunner.magic_funcs', 'pandas', 'streamlit', 'xlsxwriter', 'twilio', 'twilio.rest'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='JGRBrokerImportacao',
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
    icon=['generated-icon.png'],
)
