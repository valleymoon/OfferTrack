import multiprocessing
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
PORT_PROBE_LIMIT = 20


def _setup_import_path() -> None:
    if getattr(sys, "frozen", False):
        sys.path.insert(0, str(Path(sys._MEIPASS)))
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))


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


def _open_browser_when_ready(host: str, port: int) -> None:
    url = f"http://{host}:{port}"
    deadline = time.time() + 30
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                webbrowser.open(url)
                return
            except OSError:
                time.sleep(0.3)
    print(f"[警告] 服务启动检测超时，请手动打开浏览器访问 {url}")


def main() -> None:
    _setup_import_path()

    import uvicorn
    from app.main import app

    host = DEFAULT_HOST
    port = _find_available_port(host, DEFAULT_PORT)

    print("=" * 50)
    print(" OfferTrack 启动中")
    print(f" 地址: http://{host}:{port}")
    print(" 关闭此窗口即可停止服务")
    print("=" * 50)

    threading.Thread(
        target=_open_browser_when_ready, args=(host, port), daemon=True
    ).start()

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
