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
    Multi-candidate screen detector.

    This version does not depend on one exact stone template. It searches
    the screenshot for visually plausible object regions and returns all
    separated candidates. It uses only the captured screen image.
    """

    def __init__(self, settings: dict):
        self.min_area = settings.get("min_area", 250)
        self.max_area = settings.get("max_area", 100000)
        self.min_confidence = settings.get("min_confidence", 0.35)
        self.min_size = settings.get("min_size", 20)
        self.max_size = settings.get("max_size", 500)
        self.min_distance = settings.get("min_distance", 50)

    def detect_all(self, frame: np.ndarray) -> List[StoneDetection]:
        if frame is None or frame.size == 0:
            return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Combine edge information with local contrast. This makes the
        # detector less dependent on the exact texture of one stone.
        edges = cv2.Canny(gray, 50, 140)
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        candidates: List[StoneDetection] = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area or area > self.max_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            if w < self.min_size or h < self.min_size:
                continue
            if w > self.max_size or h > self.max_size:
                continue

            aspect = w / float(h)
            if not 0.45 <= aspect <= 2.20:
                continue

            box_area = float(max(w * h, 1))
            rectangularity = area / box_area

            # Stones tend to have a substantial amount of internal detail,
            # so also measure edge density inside the candidate box.
            roi = edges[y:y + h, x:x + w]
            if roi.size == 0:
                continue

            edge_density = float(np.count_nonzero(roi)) / float(roi.size)

            # Shape score is deliberately broad: this is a candidate finder,
            # not a final classifier.
            shape_score = min(1.0, rectangularity * 1.35)
            detail_score = min(1.0, edge_density / 0.18)
            confidence = (shape_score * 0.55) + (detail_score * 0.45)

            if confidence < self.min_confidence:
                continue

            candidates.append(
                StoneDetection(
                    center=(x + w // 2, y + h // 2),
                    confidence=confidence,
                    box=(x, y, w, h),
                )
            )

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
                distance = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5

                if distance < self.min_distance:
                    duplicate = True
                    break

            if not duplicate:
                selected.append(detection)

        return selected
