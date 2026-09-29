from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np


@dataclass
class DetectionResult:
    found: bool
    center: Optional[Tuple[int, int]] = None
    confidence: float = 0.0


@dataclass
class StoneDetection:
    center: Tuple[int, int]
    confidence: float
    box: Tuple[int, int, int, int]


class StoneDetector:
    """Multi-scale template matching with a debug mode."""

    def __init__(self, settings: dict):
        self.template_path = settings.get(
            "template_path", "stone_template.png"
        )
        self.min_confidence = settings.get("min_confidence", 0.55)
        self.min_scale = settings.get("min_scale", 0.50)
        self.max_scale = settings.get("max_scale", 1.60)
        self.scale_step = settings.get("scale_step", 0.05)
        self.min_distance = settings.get("min_distance", 45)
        self.max_detections = settings.get("max_detections", 10)

        template = cv2.imread(self.template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise FileNotFoundError(
                f"Template bulunamadi: {self.template_path}"
            )

        self.template = template
        self.template_h, self.template_w = template.shape
        self.last_best_matches: List[StoneDetection] = []

    def _match(self, frame: np.ndarray, threshold: float) -> List[StoneDetection]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        candidates: List[StoneDetection] = []

        scale = self.min_scale
        while scale <= self.max_scale + 1e-9:
            width = max(8, int(self.template_w * scale))
            height = max(8, int(self.template_h * scale))

            if width <= gray.shape[1] and height <= gray.shape[0]:
                resized = cv2.resize(
                    self.template,
                    (width, height),
                    interpolation=cv2.INTER_AREA if scale < 1.0
                    else cv2.INTER_CUBIC,
                )

                result = cv2.matchTemplate(
                    gray,
                    resized,
                    cv2.TM_CCOEFF_NORMED,
                )

                ys, xs = np.where(result >= threshold)

                for x, y in zip(xs.tolist(), ys.tolist()):
                    candidates.append(
                        StoneDetection(
                            center=(x + width // 2, y + height // 2),
                            confidence=float(result[y, x]),
                            box=(x, y, width, height),
                        )
                    )

            scale += self.scale_step

        return self._remove_duplicates(candidates)

    def detect_all(self, frame: np.ndarray) -> List[StoneDetection]:
        if frame is None or frame.size == 0:
            return []

        detections = self._match(frame, self.min_confidence)

        # Keep the strongest few matches for normal detection.
        return detections[: self.max_detections]

    def debug_matches(
        self, frame: np.ndarray, count: int = 10
    ) -> List[StoneDetection]:
        if frame is None or frame.size == 0:
            return []

        # Deliberately lower only for diagnosis. These are NOT reported
        # as real detections by detect_all().
        candidates = self._match(frame, 0.20)
        return candidates[:count]

    def detect(self, frame: np.ndarray) -> DetectionResult:
        detections = self.detect_all(frame)

        if not detections:
            return DetectionResult(False)

        best = detections[0]

        return DetectionResult(
            found=True,
            center=best.center,
            confidence=best.confidence,
        )

    def _remove_duplicates(
        self, detections: List[StoneDetection]
    ) -> List[StoneDetection]:
        detections = sorted(
            detections,
            key=lambda d: d.confidence,
            reverse=True,
        )

        selected: List[StoneDetection] = []

        for detection in detections:
            x, y = detection.center
            duplicate = False

            for existing in selected:
                ex, ey = existing.center
                distance = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5

                if distance < self.min_distance:
                    duplicate = True
                    break

            if not duplicate:
                selected.append(detection)

            if len(selected) >= self.max_detections * 5:
                break

        return selected


def draw_detection(debug: np.ndarray, detection: StoneDetection, index: int,
                   color: Tuple[int, int, int]) -> None:
    x, y, w, h = detection.box
    cx, cy = detection.center

    cv2.rectangle(
        debug, (x, y), (x + w, y + h), color, 2
    )
    cv2.circle(debug, (cx, cy), 5, color, -1)

    label = f"#{index} {detection.confidence:.2f}"
    cv2.putText(
        debug,
        label,
        (x, max(25, y - 8)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        color,
        2,
        cv2.LINE_AA,
    )
