import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routers import applications, backup, dashboard, events, questions


def _get_frontend_dist() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "frontend_dist"
    return Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="OfferTrack API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(events.router)
app.include_router(questions.router)
app.include_router(dashboard.router)
app.include_router(backup.router)


@app.post("/api/focus")
def focus_window():
    """单实例第二次启动时由 launcher 调用，把已有窗口拉到前台。

    异步执行 bring_to_front：endpoint 立即返回 200。pywebview 的 form.show() 走 GUI
    线程 marshal，连续触发会排队，sync endpoint 等它返回容易超过 launcher 端的
    timeout=2，被误判为"无法联系"。结果/失败信息靠 runtime._log 写到 offertrack.log。
    """
    import threading

    from .runtime import bring_to_front

    threading.Thread(target=bring_to_front, daemon=True).start()
    return {"ok": True}


FRONTEND_DIST = _get_frontend_dist()

if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
else:

    @app.get("/")
    def root():
        return {"message": "Hello OfferTrack"}
