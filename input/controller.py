import ctypes
import time
from ctypes import wintypes


user32 = ctypes.windll.user32

MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010


class InputController:
    """Windows user-level mouse input helper."""

    def __init__(self):
        pass

    @staticmethod
    def move_mouse(x: int, y: int, duration: float = 0.15) -> None:
        start_x, start_y = 0, 0
        point = wintypes.POINT()
        if user32.GetCursorPos(ctypes.byref(point)):
            start_x, start_y = point.x, point.y

        steps = max(1, int(duration * 60))
        for i in range(1, steps + 1):
            t = i / steps
            user32.SetCursorPos(
                int(start_x + (x - start_x) * t),
                int(start_y + (y - start_y) * t),
            )
            time.sleep(duration / steps)

    @staticmethod
    def click() -> None:
        InputController.click_at(0, 0)

    @staticmethod
    def click_at(x: int, y: int) -> None:
        """Send a standard Windows left-button click at screen coordinates."""
        InputController.move_mouse(x, y)
        time.sleep(0.10)

        MOUSEEVENTF_LEFTDOWN = 0x0002
        MOUSEEVENTF_LEFTUP = 0x0004

        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.08)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
