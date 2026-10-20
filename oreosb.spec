# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — build EXE / Linux binary
# pyinstaller oreosb.spec

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('main.py', '.'),
        ('multi_token.py', '.'),
        ('config.json', '.'),
        ('.env.example', '.'),
        ('cogs', 'cogs'),
        ('evasion', 'evasion'),
        ('requirements.txt', '.'),
        ('run.sh', '.'),
    ],
    hiddenimports=[
        'discord',
        'discord.ext',
        'discord.ext.commands',
        'aiohttp',
        'dotenv',
        'colorama',
        'PIL',
        'httpx',
    ],
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
    name='OreoSB',
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
