"""统一可写目录 / 资源路径解析。

设计目标：
- 打包后默认写到 %LOCALAPPDATA%\\OfferTrack\\（即使 exe 放到 Program Files 也能跑）
- 便携模式：exe 同目录存在 portable.flag 时，回退到 exe 旁的 data/
- 开发模式（非 frozen）：用项目根目录下的 data/，跟旧行为一致
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path


PORTABLE_FLAG = "portable.flag"


def _exe_dir() -> Path:
    """打包后 exe 所在目录；开发模式返回项目根。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent


def _localappdata_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "OfferTrack"
    # 兜底：用户 home/.OfferTrack
    return Path.home() / ".OfferTrack"


@lru_cache(maxsize=1)
def app_data_dir() -> Path:
    """所有可写文件（DB / 日志 / 锁 / 窗口状态）统一从这里取。"""
    if getattr(sys, "frozen", False):
        # 打包后：默认 LOCALAPPDATA，遇到便携标志则用 exe 旁
        if (_exe_dir() / PORTABLE_FLAG).exists():
            target = _exe_dir() / "data"
        else:
            target = _localappdata_dir()
    else:
        # 开发模式：保留旧行为
        target = _exe_dir() / "data"

    target.mkdir(parents=True, exist_ok=True)
    return target


def db_path() -> Path:
    return app_data_dir() / "offertrack.db"


def log_path() -> Path:
    return app_data_dir() / "offertrack.log"


def runtime_json_path() -> Path:
    """单实例运行期信息（pid + uvicorn port），用于第二实例联系第一实例。"""
    return app_data_dir() / "runtime.json"


def window_state_path() -> Path:
    return app_data_dir() / "window_state.json"


def bundled_resource(name: str) -> Path:
    """读 PyInstaller 打包进来的只读资源（如 app.ico）。

    - 打包后从 sys._MEIPASS 取（或 exe 旁，spec datas 决定）
    - 开发模式从项目 assets/ 取
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidate = Path(meipass) / name
            if candidate.exists():
                return candidate
        candidate = _exe_dir() / name
        if candidate.exists():
            return candidate
    candidate = _exe_dir() / "assets" / name
    return candidate
