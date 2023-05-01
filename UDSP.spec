# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, get_deps_all, hookspath, runtime_hooks

a = Analysis(
    ['src/UltimateDrumScorerPro.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    hookspath=hookspath(),
    runtime_hooks=runtime_hooks(),
    **get_deps_all()
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    Tree('src/'),
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='UDSP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
