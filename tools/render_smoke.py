"""Native Windows window and geometry-capture helpers for Ornith smokes."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path
import subprocess
import time

from PIL import ImageStat

from window_capture import capture_client_image


WM_CLOSE = 0x0010
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
HWND_TOPMOST = -1

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND
user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetClientRect.restype = wintypes.BOOL
user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
user32.ClientToScreen.restype = wintypes.BOOL
user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
user32.SetWindowPos.restype = wintypes.BOOL
user32.BringWindowToTop.argtypes = [wintypes.HWND]
user32.BringWindowToTop.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL


def wait_for_window(title: str, process: subprocess.Popen[bytes], timeout: float) -> int:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Game exited early with code {process.returncode}")
        hwnd = user32.FindWindowW(None, title)
        if hwnd:
            return hwnd
        time.sleep(0.1)
    raise TimeoutError(f"Window {title!r} did not appear within {timeout} seconds")


def capture_client(
    hwnd: int, destination: Path, expectation: str
) -> tuple[tuple[int, int], tuple[int, int, int]]:
    if expectation != "geometry":
        raise ValueError("Ornith captures support only the geometry expectation")
    if not user32.SetWindowPos(
        hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.25)

    image = capture_client_image(hwnd)
    image.save(destination)
    center = image.getpixel((image.width // 2, image.height // 2))
    deviation = ImageStat.Stat(image).stddev
    background = (63, 108, 149)
    pixels = list(image.get_flattened_data())
    changed = sum(
        max(abs(pixel[channel] - background[channel]) for channel in range(3)) > 30
        for pixel in pixels
    ) / (image.width * image.height)
    if not 0.03 < changed < 0.95:
        raise AssertionError(f"Unexpected geometry coverage: {changed:.1%}")
    if max(deviation) < 20:
        raise AssertionError(f"Geometry frame lacks visual variation: {deviation}")
    print(f"Geometry coverage: {changed:.1%}")
    return image.size, center
