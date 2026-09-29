from dataclasses import dataclass, field
from typing import Optional, Tuple

import cv2
import mss
import numpy as np

from config import BOT_CONFIG


@dataclass
class Screen:
    last_origin: Tuple[int, int] = field(default=(0, 0), init=False)

    def capture_game_region(self) -> Optional[np.ndarray]:
        region = BOT_CONFIG["region"]

        with mss.mss() as sct:
            monitor = region or sct.monitors[1]
            raw = np.array(sct.grab(monitor))

            self.last_origin = (
                int(monitor["left"]),
                int(monitor["top"]),
            )

        return cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
