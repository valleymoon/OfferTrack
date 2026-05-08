"""OfferTrack 桌面壳：

1. 命名互斥锁做单实例；第二实例把第一实例窗口拉到前台后退出
2. windowed 模式下，stdout/stderr 重定向到日志文件
3. uvicorn 在后台线程跑，主线程阻塞在 pywebview 窗口
4. 关窗口 → 优雅停止 uvicorn → 清理 runtime.json → 释放互斥锁 → 进程退出
5. 窗口大小/位置在关闭时持久化，下次启动恢复
"""

from __future__ import annotations

import json
import multiprocessing
import os
import socket
import sys
import threading
import time
import urllib.request
from pathlib import Path
from typing import Optional


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
PORT_PROBE_LIMIT = 20
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 820
MIN_WIDTH = 960
MIN_HEIGHT = 600
MUTEX_NAME = "Local\\OfferTrack-SingleInstance"


# ---------- 路径 / import 准备 ----------


def _setup_import_path() -> None:
    if getattr(sys, "frozen", False):
        sys.path.insert(0, str(Path(sys._MEIPASS)))
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))


# ---------- 日志重定向（必须最早调用） ----------


def _setup_log_redirect() -> None:
    """windowed 模式 sys.stdout/stderr 是 None，uvicorn / print 都会崩。
    重定向到 LOCALAPPDATA/OfferTrack/offertrack.log。"""
    if not getattr(sys, "frozen", False):
        return
    try:
        from app.paths import log_path
    except Exception:
        return
    try:
        f = open(log_path(), "a", encoding="utf-8", buffering=1)
    except OSError:
        return
    sys.stdout = f
    sys.stderr = f


# ---------- 单实例互斥锁 ----------


class _SingleInstance:
    def __init__(self) -> None:
        self._handle = None

    def acquire(self) -> bool:
        """True 表示我是第一个实例；False 表示已有实例在跑。"""
        if sys.platform != "win32":
            return True
        try:
            import win32event
            import win32api
            import winerror
        except ImportError:
            return True
        self._handle = win32event.CreateMutex(None, False, MUTEX_NAME)
        return win32api.GetLastError() != winerror.ERROR_ALREADY_EXISTS

    def release(self) -> None:
        if self._handle is None:
            return
        try:
            import win32api
            win32api.CloseHandle(self._handle)
        except Exception:
            pass
        finally:
            self._handle = None


def _try_focus_existing() -> bool:
    """读 runtime.json 联系第一实例，把它拉到前台。"""
    try:
        from app.paths import runtime_json_path
    except Exception:
        return False
    p = runtime_json_path()
    if not p.exists():
        return False
    try:
        info = json.loads(p.read_text(encoding="utf-8"))
        port = int(info["port"])
        pid = int(info["pid"])
    except (OSError, ValueError, KeyError):
        return False

    # 把"前台抓取权限"让渡给第一实例，否则它的 SetForegroundWindow 大概率失败
    if sys.platform == "win32":
        try:
            import win32process
            win32process.AllowSetForegroundWindow(pid)
        except Exception:
            pass

    url = f"http://{DEFAULT_HOST}:{port}/api/focus"
    try:
        req = urllib.request.Request(url, method="POST")
        # 显式 no-proxy：若机器设了 HTTP_PROXY（Clash/V2Ray 之类），urllib 默认会把
        # 127.0.0.1:8000 也走代理，绕一圈本地代理常导致 timeout/拒绝
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=2):
            return True
    except Exception:
        return False


# ---------- runtime.json ----------


def _write_runtime_json(port: int) -> None:
    from app.paths import runtime_json_path
    runtime_json_path().write_text(
        json.dumps({"pid": os.getpid(), "port": port}),
        encoding="utf-8",
    )


def _cleanup_runtime_json() -> None:
    try:
        from app.paths import runtime_json_path
        runtime_json_path().unlink(missing_ok=True)
    except Exception:
        pass


# ---------- 端口选择 / 等待就绪 ----------


def _find_available_port(host: str, start_port: int) -> int:
    for offset in range(PORT_PROBE_LIMIT):
        port = start_port + offset
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return port
    raise RuntimeError(
        f"未找到可用端口（{start_port}-{start_port + PORT_PROBE_LIMIT - 1} 全部被占用）"
    )


def _wait_for_port(host: str, port: int, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                return True
            except OSError:
                time.sleep(0.2)
    return False


# ---------- 窗口状态持久化 ----------


def _load_window_state() -> dict:
    try:
        from app.paths import window_state_path
        data = json.loads(window_state_path().read_text(encoding="utf-8"))
    except Exception:
        return {"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT, "x": None, "y": None}

    def _coerce(v, default=None, lo=None, hi=None):
        if v is None:
            return default
        try:
            iv = int(v)
        except (TypeError, ValueError):
            return default
        if lo is not None and iv < lo:
            return default
        if hi is not None and iv > hi:
            return default
        return iv

    return {
        "width": _coerce(data.get("width"), DEFAULT_WIDTH, MIN_WIDTH, 8192),
        "height": _coerce(data.get("height"), DEFAULT_HEIGHT, MIN_HEIGHT, 8192),
        "x": _coerce(data.get("x"), None, -8192, 16384),
        "y": _coerce(data.get("y"), None, -8192, 16384),
    }


def _save_window_state(window) -> None:
    try:
        from app.paths import window_state_path
        state = {
            "width": int(getattr(window, "width", DEFAULT_WIDTH) or DEFAULT_WIDTH),
            "height": int(getattr(window, "height", DEFAULT_HEIGHT) or DEFAULT_HEIGHT),
            "x": int(getattr(window, "x", 0) or 0),
            "y": int(getattr(window, "y", 0) or 0),
        }
        window_state_path().write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass


# ---------- 资源 ----------


def _icon_path() -> Optional[str]:
    try:
        from app.paths import bundled_resource
    except Exception:
        return None
    p = bundled_resource("app.ico")
    return str(p) if p.exists() else None


# ---------- 主流程 ----------


def main() -> None:
    _setup_import_path()
    _setup_log_redirect()

    # 1. 单实例锁
    instance = _SingleInstance()
    is_first = instance.acquire()
    if not is_first:
        if _try_focus_existing():
            sys.exit(0)
        # 联系不上已有实例（可能是僵尸 runtime.json），直接退出避免双进程
        print("已有 OfferTrack 实例在运行，但无法联系。请通过任务管理器结束 OfferTrack.exe 后重试。")
        sys.exit(1)

    # 2. 后端
    import uvicorn
    from app.main import app
    from app.runtime import register_window

    port = _find_available_port(DEFAULT_HOST, DEFAULT_PORT)
    config = uvicorn.Config(
        app,
        host=DEFAULT_HOST,
        port=port,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    if not _wait_for_port(DEFAULT_HOST, port, timeout=30):
        print(f"[X] 后端未在 30 秒内监听 {DEFAULT_HOST}:{port}")
        instance.release()
        sys.exit(1)

    _write_runtime_json(port)

    # 3. 窗口
    import webview

    state = _load_window_state()
    create_kwargs = dict(
        title="OfferTrack",
        url=f"http://{DEFAULT_HOST}:{port}",
        width=state["width"],
        height=state["height"],
        min_size=(MIN_WIDTH, MIN_HEIGHT),
    )
    if state["x"] is not None and state["y"] is not None:
        create_kwargs["x"] = state["x"]
        create_kwargs["y"] = state["y"]

    window = webview.create_window(**create_kwargs)
    register_window(window)

    def _on_closing():
        _save_window_state(window)

    # pywebview 5.x 用 += 订阅
    try:
        window.events.closing += _on_closing
    except Exception:
        # 兼容旧 API
        try:
            window.events.closing.connect(_on_closing)
        except Exception:
            pass

    icon = _icon_path()
    try:
        if icon:
            webview.start(icon=icon)
        else:
            webview.start()
    finally:
        # 4. 清理
        try:
            server.should_exit = True
        except Exception:
            pass
        server_thread.join(timeout=1.5)
        _cleanup_runtime_json()
        instance.release()
        # 兜底：不管 uvicorn 是否真停了，强退避免僵尸
        os._exit(0)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
