import ctypes
import time
from ctypes import wintypes


user32 = ctypes.windll.user32

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


class InputController:
    """Windows user-level mouse input helper for UI testing."""

    @staticmethod
    def move_mouse(x: int, y: int, duration: float = 0.18) -> None:
        point = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(point))

        start_x, start_y = point.x, point.y
        distance = ((x - start_x) ** 2 + (y - start_y) ** 2) ** 0.5
        steps = max(8, min(30, int(distance / 25)))

        for i in range(1, steps + 1):
            t = i / steps
            eased = t * t * (3.0 - 2.0 * t)
            px = int(start_x + (x - start_x) * eased)
            py = int(start_y + (y - start_y) * eased)
            user32.SetCursorPos(px, py)
            time.sleep(duration / steps)

    @staticmethod
    def click() -> None:
        InputController.click_at(0, 0)

    @staticmethod
    def click_at(x: int, y: int) -> None:
        InputController.move_mouse(x, y, duration=0.18)
        time.sleep(0.40)
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.20)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
