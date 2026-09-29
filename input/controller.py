import pyautogui


class InputController:
    """Normal-user-level input helper. No client injection or protection bypass."""

    @staticmethod
    def move_mouse(x: int, y: int, duration: float = 0.15) -> None:
        pyautogui.moveTo(x, y, duration=duration)

    @staticmethod
    def click() -> None:
        pyautogui.click()

    @staticmethod
    def click_at(x: int, y: int) -> None:
        """Select a visible target using an ordinary mouse click."""
        pyautogui.click(x=x, y=y)
