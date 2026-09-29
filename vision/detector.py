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
    """
    Multi-scale template matcher for the Metin stone.

    Detection is based on the supplied stone_template.png rather than
    generic edges/shapes, so unrelated UI and world objects are much less
    likely to be selected.
    """

    def __init__(self, settings: dict):
        self.template_path = settings.get(
            "template_path", "stone_template.png"
        )
        self.min_confidence = settings.get("min_confidence", 0.55)
        self.min_scale = settings.get("min_scale", 0.60)
        self.max_scale = settings.get("max_scale", 1.40)
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

    def detect_all(self, frame: np.ndarray) -> List[StoneDetection]:
        if frame is None or frame.size == 0:
            return []

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
                    interpolation=cv2.INTER_AREA
                    if scale < 1.0
                    else cv2.INTER_CUBIC,
                )

                result = cv2.matchTemplate(
                    gray,
                    resized,
                    cv2.TM_CCOEFF_NORMED,
                )

                ys, xs = np.where(result >= self.min_confidence)

                for x, y in zip(xs.tolist(), ys.tolist()):
                    confidence = float(result[y, x])
                    center = (
                        x + width // 2,
                        y + height // 2,
                    )

                    candidates.append(
                        StoneDetection(
                            center=center,
                            confidence=confidence,
                            box=(x, y, width, height),
                        )
                    )

            scale += self.scale_step

        return self._remove_duplicates(candidates)

    def detect(self, frame: np.ndarray) -> DetectionResult:
        detections = self.detect_all(frame)

        if not detections:
            return DetectionResult(False)

        best = max(detections, key=lambda d: d.confidence)

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

                distance = (
                    (x - ex) ** 2 + (y - ey) ** 2
                ) ** 0.5

                if distance < self.min_distance:
                    duplicate = True
                    break

            if not duplicate:
                selected.append(detection)

            if len(selected) >= self.max_detections:
                break

        return selected
