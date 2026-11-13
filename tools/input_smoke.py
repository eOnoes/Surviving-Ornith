"""Native Windows input helpers shared by Ornith smoke tests."""

from __future__ import annotations

import ctypes
from ctypes import wintypes

from render_smoke import user32


WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
user32.SetCursorPos.restype = wintypes.BOOL


def post_message(hwnd: int, message: int, wparam: int = 0, lparam: int = 0) -> None:
    if not user32.PostMessageW(hwnd, message, wparam, lparam):
        raise ctypes.WinError(ctypes.get_last_error())


def move_cursor_to_client_center(hwnd: int) -> None:
    rectangle = wintypes.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rectangle)):
        raise ctypes.WinError(ctypes.get_last_error())
    point = wintypes.POINT(
        (rectangle.left + rectangle.right) // 2,
        (rectangle.top + rectangle.bottom) // 2,
    )
    if not user32.ClientToScreen(hwnd, ctypes.byref(point)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not user32.SetCursorPos(point.x, point.y):
        raise ctypes.WinError(ctypes.get_last_error())
