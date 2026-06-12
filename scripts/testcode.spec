# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['testcode_core', 'testcode_core.agent', 'testcode_core.agent.context', 'testcode_core.agent.loop', 'testcode_core.database', 'testcode_core.database.engine', 'testcode_core.database.models', 'testcode_core.session', 'testcode_core.session.store', 'testcode_core.tools', 'testcode_core.tools.registry', 'testcode_core.tools.bash', 'testcode_core.tools.file_read', 'testcode_core.tools.file_write', 'testcode_core.tools.file_edit', 'testcode_core.tools.glob_tool', 'testcode_core.tools.grep_tool', 'testcode_core.tools.web_fetch', 'testcode_llm', 'testcode_llm.provider', 'testcode_llm.registry', 'testcode_llm.types', 'testcode_llm.providers', 'testcode_llm.providers._anthropic', 'testcode_llm.providers._openai', 'testcode_cli', 'testcode_cli.main', 'testcode_tui', 'testcode_tui.app', 'testcode_tui.screens', 'testcode_tui.screens.main_screen', 'testcode_tui.widgets', 'testcode_tui.widgets.chat_view', 'testcode_tui.widgets.input_area', 'testcode_tui.widgets.session_list', 'testcode_tui.widgets.status_bar', 'testcode_server', 'testcode_server.app', 'testcode_sdk', 'testcode_sdk.client', 'testcode_sdk.types', 'testcode_plugin', 'testcode_plugin.hooks', 'testcode_plugin.decorators', 'testcode_plugin.loader', 'testcode_desktop', 'testcode_desktop.main', 'sqlalchemy', 'sqlalchemy.ext.asyncio', 'aiosqlite', 'fastapi', 'uvicorn', 'pydantic', 'sse_starlette', 'textual', 'textual_serve', 'textual_serve.server', 'typer', 'httpx'],
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
    name='testcode',
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
