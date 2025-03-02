# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Enhanced data collection
datas = [
    ('icons/*.ico', 'icons'),     # Only include .ico files
    ('app/*.py', 'app'),       # Include all Python files recursively
    ('model/*', 'model'),      # Include all model files recursively
]

# Collect all pydantic submodules properly
pydantic_submodules = collect_submodules('pydantic')
langchain_core_submodules = collect_submodules('langchain_core')
langchain_ollama_submodules = collect_submodules('langchain_ollama')

# Expanded hidden imports with common dependencies
hidden_imports = [
    'pydantic',
    'pydantic.deprecated.decorator',  # Add the specific missing module
    *pydantic_submodules,  # Include all pydantic submodules
    'langchain_core',
    *langchain_core_submodules,
    'langchain_ollama',
    *langchain_ollama_submodules,
    'speech_recognition',
    'markdown',
    'pygments',
    'pygments.lexers.*',
    'pygments.formatters.*',
    'sqlite3',
    'asyncio',
    'aiohttp',
    'typing_extensions',
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.dirname(os.path.abspath(SPEC))],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy', 'tkinter',
        'PyQt5', 'wx', 'test', '_pytest',  # Additional excludes
    ],
    noarchive=False,
    optimize=2,
)

# Compress with higher efficiency
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Madick AI Chatbot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip symbols to reduce size
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'python*.dll',
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/favicon.ico',
    uac_admin=False,
)

# Optimized collection
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'python*.dll',
    ],
    name='Madick AI Chatbot',
)
