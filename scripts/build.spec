# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for TestCode cross-platform build."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PACKAGES = [
    "testcode_core", "testcode_llm", "testcode_cli",
    "testcode_tui", "testcode_server", "testcode_sdk",
    "testcode_plugin", "testcode_desktop",
]

a = Analysis(
    ['launcher.py'],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        (str(PROJECT_ROOT / "pyproject.toml"), "."),
    ],
    hiddenimports=[
        # TestCode packages
        *PACKAGES,
        f"{PACKAGES[0]}.agent",
        f"{PACKAGES[0]}.agent.context",
        f"{PACKAGES[0]}.agent.loop",
        f"{PACKAGES[0]}.database",
        f"{PACKAGES[0]}.database.engine",
        f"{PACKAGES[0]}.database.models",
        f"{PACKAGES[0]}.session",
        f"{PACKAGES[0]}.session.store",
        f"{PACKAGES[0]}.tools",
        f"{PACKAGES[0]}.tools.registry",
        f"{PACKAGES[0]}.tools.bash",
        f"{PACKAGES[0]}.tools.file_read",
        f"{PACKAGES[0]}.tools.file_write",
        f"{PACKAGES[0]}.tools.file_edit",
        f"{PACKAGES[0]}.tools.glob_tool",
        f"{PACKAGES[0]}.tools.grep_tool",
        f"{PACKAGES[0]}.tools.web_fetch",
        f"{PACKAGES[1]}.provider",
        f"{PACKAGES[1]}.registry",
        f"{PACKAGES[1]}.types",
        f"{PACKAGES[1]}.providers",
        f"{PACKAGES[1]}.providers._anthropic",
        f"{PACKAGES[1]}.providers._openai",
        f"{PACKAGES[3]}.app",
        f"{PACKAGES[3]}.screens",
        f"{PACKAGES[3]}.screens.main_screen",
        f"{PACKAGES[3]}.widgets",
        f"{PACKAGES[3]}.widgets.chat_view",
        f"{PACKAGES[3]}.widgets.input_area",
        f"{PACKAGES[3]}.widgets.session_list",
        f"{PACKAGES[3]}.widgets.status_bar",
        f"{PACKAGES[4]}.app",
        f"{PACKAGES[5]}.client",
        f"{PACKAGES[5]}.types",
        f"{PACKAGES[6]}.hooks",
        f"{PACKAGES[6]}.decorators",
        f"{PACKAGES[6]}.loader",
        f"{PACKAGES[7]}.main",
        # Third-party
        "sqlalchemy",
        "sqlalchemy.ext.asyncio",
        "aiosqlite",
        "fastapi",
        "uvicorn",
        "sse_starlette",
        "textual",
        "textual_serve",
        "textual_serve.server",
        "httpx",
        "typer",
        "pydantic",
        "anyio",
        "starlette",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
        "PIL",
        "PyQt5",
        "PySide2",
    ],
    noarchive=False,
    module_collection_mode={
        "testcode_core": "pyz",
        "testcode_llm": "pyz",
        "testcode_cli": "pyz",
        "testcode_tui": "pyz",
        "testcode_server": "pyz",
        "testcode_sdk": "pyz",
        "testcode_plugin": "pyz",
        "testcode_desktop": "pyz",
    },
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="testcode",
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

if sys.platform == "darwin":
    COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        name="TestCode",
    )
