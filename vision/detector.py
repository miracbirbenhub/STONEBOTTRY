from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass
class DetectionResult:
    found: bool
    center: Optional[Tuple[int, int]] = None
    confidence: float = 0.0


class StoneDetector:
    """
    First-stage visual detector.

    This deliberately does not guess from process memory. It works on a
    screenshot and will be upgraded with a client-specific stone template
    after we capture one from the user's game.
    """

    def __init__(self, settings: dict):
        self.min_area = settings["min_area"]
        self.max_area = settings["max_area"]
        self.min_confidence = settings["min_confidence"]

    def detect(self, frame: np.ndarray) -> DetectionResult:
        if frame is None or frame.size == 0:
            return DetectionResult(False)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Edge map is only a diagnostic heuristic for now.
        edges = cv2.Canny(blurred, 80, 160)
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        best = None
        best_score = 0.0

        for contour in contours:
            area = cv2.contourArea(contour)
            if not (self.min_area <= area <= self.max_area):
                continue

            x, y, w, h = cv2.boundingRect(contour)
            if h == 0:
                continue

            aspect = w / h
            if not 0.45 <= aspect <= 2.2:
                continue

            rectangularity = area / float(max(w * h, 1))
            score = min(1.0, rectangularity * 1.25)

            if score > best_score:
                best_score = score
                best = (x, y, w, h)

        if best is None or best_score < self.min_confidence:
            return DetectionResult(False)

        x, y, w, h = best
        return DetectionResult(
            True,
            center=(x + w // 2, y + h // 2),
            confidence=best_score,
        )
