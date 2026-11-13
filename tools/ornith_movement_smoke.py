"""Playtest Ornith movement, stance presentation, recoil, and tool swings."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import time

from input_smoke import WM_KEYDOWN, WM_KEYUP, post_message
from render_smoke import SWP_NOZORDER, WM_CLOSE, capture_client, user32, wait_for_window


TITLE = "Surviving Ornith — UBE nerd 0.1"
VK = {
    "SPACE": 0x20,
    "CTRL": 0x11,
    "Z": 0x5A,
    "SHIFT": 0x10,
    "W": 0x57,
    "V": 0x56,
    "1": 0x31,
    "4": 0x34,
}
SCAN = {"SPACE": 0x39, "CTRL": 0x1D, "Z": 0x2C, "SHIFT": 0x2A, "W": 0x11}
WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0201, 0x0202


def key(hwnd: int, name: str, pressed: bool) -> None:
    scan_code = SCAN.get(name, 0)
    key_data = 1 | (scan_code << 16) | (0 if pressed else 0xC0000000)
    post_message(hwnd, WM_KEYDOWN if pressed else WM_KEYUP, VK[name], key_data)


def tap(hwnd: int, name: str, pause: float = 0.35) -> None:
    key(hwnd, name, True)
    time.sleep(0.09)
    key(hwnd, name, False)
    time.sleep(pause)


def click(hwnd: int) -> None:
    post_message(hwnd, WM_LBUTTONDOWN)
    time.sleep(0.07)
    post_message(hwnd, WM_LBUTTONUP)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, default=Path("target/release/surviving-ornith.exe"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/ornith-movement-smoke"))
    args = parser.parse_args()
    executable = args.executable.resolve()
    workspace = executable.parent.parent.parent
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    stdout_path, stderr_path = output / "stdout.log", output / "stderr.log"

    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen([str(executable)], cwd=workspace, stdout=stdout, stderr=stderr)
        try:
            hwnd = wait_for_window(TITLE, process, timeout=20)
            if not user32.SetWindowPos(hwnd, 0, 100, 80, 1280, 720, SWP_NOZORDER):
                raise OSError("Could not resize Ornith window")
            time.sleep(9)
            capture_client(hwnd, output / "01-standing.png", "geometry")

            tap(hwnd, "CTRL")
            capture_client(hwnd, output / "02-crouching.png", "geometry")
            tap(hwnd, "Z")
            capture_client(hwnd, output / "03-prone.png", "geometry")
            tap(hwnd, "V")
            capture_client(hwnd, output / "04-third-person-prone.png", "geometry")
            tap(hwnd, "Z")

            key(hwnd, "SPACE", True)
            time.sleep(0.12)
            key(hwnd, "SPACE", False)
            capture_client(hwnd, output / "05-jumping.png", "geometry")
            time.sleep(1.0)

            key(hwnd, "W", True)
            key(hwnd, "SHIFT", True)
            time.sleep(0.75)
            capture_client(hwnd, output / "06-sprinting.png", "geometry")
            key(hwnd, "SHIFT", False)
            key(hwnd, "W", False)
            time.sleep(0.4)
            tap(hwnd, "V", 0.2)
            tap(hwnd, "V", 0.3)

            tap(hwnd, "4", 0.15)
            click(hwnd)
            time.sleep(0.1)
            capture_client(hwnd, output / "07-axe-swing.png", "geometry")
            time.sleep(0.5)
            tap(hwnd, "1", 0.15)
            click(hwnd)
            time.sleep(0.06)
            capture_client(hwnd, output / "08-rifle-recoil.png", "geometry")
            time.sleep(0.5)

            post_message(hwnd, WM_CLOSE)
            code = process.wait(timeout=8)
            if code != 0:
                raise RuntimeError(f"Ornith returned exit code {code}")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)

    diagnostics = stdout_path.read_text(encoding="utf-8")
    for stance in ("Crouching", "Prone", "Standing"):
        if f"stance={stance}" not in diagnostics:
            raise AssertionError(f"Missing Ornith stance transition: {stance}")
    if diagnostics.count("character stance changed") != 3:
        raise AssertionError("Ctrl/Z did not complete the expected three stance transitions")
    if diagnostics.count("character jumped") != 1:
        raise AssertionError("Space did not produce one grounded jump")
    if "sprinting=true" not in diagnostics or "sprinting=false" not in diagnostics:
        raise AssertionError("Shift+W did not produce sprint start/stop events")
    for effect in ("effect=swing", "effect=rifle"):
        if effect not in diagnostics:
            raise AssertionError(f"Missing action audio request: {effect}")
    if stderr_path.read_text(encoding="utf-8").strip():
        raise AssertionError("Ornith wrote to standard error")
    print("Ornith movement smoke: crouch, prone, third-person stance, jump, sprint, axe swing, rifle recoil, clean exit")
    print(f"Evidence written to {output}")


if __name__ == "__main__":
    main()
