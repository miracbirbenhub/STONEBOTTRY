from dataclasses import dataclass
from typing import Optional

import cv2
import mss
import numpy as np

from config import BOT_CONFIG


@dataclass
class Screen:
    def capture_game_region(self) -> Optional[np.ndarray]:
        region = BOT_CONFIG["region"]

        with mss.mss() as sct:
            monitor = region or sct.monitors[1]
            raw = np.array(sct.grab(monitor))

        return cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
