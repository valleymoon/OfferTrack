"""桌面壳运行时状态：跟 launcher.py 共享 webview 窗口实例，提供"拉前台"能力。

后端 API 跑在子线程里，但 pywebview 已经把 GUI 操作的线程封送做好了，所以可以
直接调 form.restore() / form.show()。Win32 SetForegroundWindow 受系统的
"前台抢占限制"约束，单调它经常失败 —— 用 AttachThreadInput 把当前线程跟前台
窗口的输入队列临时绑定，可绕开限制。
"""

from __future__ import annotations

import sys
from typing import Any, Optional


_window: Optional[Any] = None


def register_window(window: Any) -> None:
    """launcher 创建好 webview.Window 后调一次，把实例挂到全局。"""
    global _window
    _window = window


def _log(msg: str) -> None:
    """轻量日志：launcher 已经把 stdout 重定向到 offertrack.log，print 即可。"""
    try:
        print(f"[runtime] {msg}", flush=True)
    except Exception:
        pass


# ---------- 句柄查找 ----------


def _get_form() -> Optional[Any]:
    """从 pywebview 的内部 BrowserView 实例字典里拿 WinForms Form 对象。"""
    try:
        from webview.platforms.winforms import BrowserView
    except Exception as e:
        _log(f"import BrowserView failed: {e}")
        return None
    instances = getattr(BrowserView, "instances", None)
    if not instances:
        return None
    # 我们只有一个窗口
    return next(iter(instances.values()), None)


def _hwnd_via_form() -> Optional[int]:
    form = _get_form()
    if form is None:
        return None
    try:
        return int(form.Handle.ToInt32())
    except Exception as e:
        _log(f"form.Handle failed: {e}")
        return None


def _hwnd_via_findwindow(title: str = "OfferTrack") -> Optional[int]:
    try:
        import win32gui
    except ImportError:
        return None
    hwnd = win32gui.FindWindow(None, title)
    return hwnd if hwnd else None


# ---------- 拉前台 ----------


def bring_to_front() -> bool:
    """两条腿：先用 pywebview 自己的 form.show() 做线程安全的恢复+激活；
    再用 Win32 兜底，配 AttachThreadInput 绕开前台抢占限制。"""
    if sys.platform != "win32":
        return False

    # 路径 A：用 pywebview 自己的 API（GUI 线程封送由它处理）
    form = _get_form()
    if form is not None:
        try:
            form.restore()  # 若最小化则还原
        except Exception as e:
            _log(f"form.restore failed: {e}")
        try:
            form.show()  # show + Activate
        except Exception as e:
            _log(f"form.show failed: {e}")

    # 路径 B：Win32 兜底（pywebview 的 Activate 在某些焦点场景下抢不到前台）
    hwnd = _hwnd_via_form() or _hwnd_via_findwindow()
    if not hwnd:
        _log("hwnd not found, can not force foreground")
        # 即使没拿到 hwnd，前面 form.show() 也可能已经把窗口显示出来
        return form is not None

    try:
        import win32api
        import win32con
        import win32gui
        import win32process
    except ImportError as e:
        _log(f"pywin32 import failed: {e}")
        return True  # 至少 form.show() 已经尝试过了

    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    else:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

    # AttachThreadInput trick：把当前线程跟前台窗口所属线程的输入队列临时绑定，
    # 这样 SetForegroundWindow 不会被 Win 默认的"非前台进程禁止抢前台"挡掉
    fg_hwnd = win32gui.GetForegroundWindow()
    cur_thread = win32api.GetCurrentThreadId()
    fg_thread = 0
    attached = False
    try:
        if fg_hwnd:
            fg_thread = win32process.GetWindowThreadProcessId(fg_hwnd)[0]
        if fg_thread and fg_thread != cur_thread:
            try:
                win32process.AttachThreadInput(fg_thread, cur_thread, True)
                attached = True
            except Exception as e:
                _log(f"AttachThreadInput failed: {e}")
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            _log(f"SetForegroundWindow failed: {e}; fallback to BringWindowToTop")
            try:
                win32gui.BringWindowToTop(hwnd)
            except Exception as ee:
                _log(f"BringWindowToTop failed too: {ee}")
        # 再走一遍以稳态显示
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        except Exception:
            pass
    finally:
        if attached:
            try:
                win32process.AttachThreadInput(fg_thread, cur_thread, False)
            except Exception:
                pass

    _log(f"bring_to_front done (hwnd={hwnd})")
    return True
