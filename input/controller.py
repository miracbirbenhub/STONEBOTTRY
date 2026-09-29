import time

import pyautogui


class InputController:
    """Normal-user-level mouse input helper."""

    def __init__(self):
        pyautogui.PAUSE = 0.05
        pyautogui.FAILSAFE = True

    @staticmethod
    def move_mouse(x: int, y: int, duration: float = 0.15) -> None:
        pyautogui.moveTo(x, y, duration=duration)

    @staticmethod
    def click() -> None:
        pyautogui.click()

    @staticmethod
    def click_at(x: int, y: int) -> None:
        """Move to a visible target and send an explicit left-button click."""
        pyautogui.moveTo(x, y, duration=0.15)
        time.sleep(0.10)
        pyautogui.mouseDown(button="right")
        time.sleep(0.08)
        pyautogui.mouseUp(button="left")
