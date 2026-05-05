# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

PROJECT_ROOT = Path(SPECPATH).resolve()
BACKEND_APP_DIR = PROJECT_ROOT / "backend" / "app"
FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "dist"

datas = [
    (str(BACKEND_APP_DIR), "app"),
]

if FRONTEND_DIST_DIR.exists():
    datas.append((str(FRONTEND_DIST_DIR), "frontend_dist"))

hiddenimports = [
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.protocols.websockets.wsproto_impl",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
    "app",
    "app.main",
    "app.database",
    "app.models",
    "app.schemas",
    "app.routers",
    "app.routers.applications",
    "app.routers.events",
    "app.routers.questions",
    "app.routers.dashboard",
    "app.routers.backup",
    "sqlalchemy.dialects.sqlite",
]


a = Analysis(
    ["launcher.py"],
    pathex=[str(PROJECT_ROOT), str(PROJECT_ROOT / "backend")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="OfferTrack",
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
