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
    template_index: int = 0


class StoneDetector:
    """Multi-template, multi-scale visual detector for Metin stones."""

    def __init__(self, settings: dict):
        paths = settings.get("template_paths")

        if not paths:
            old_path = settings.get("template_path", "stone_template.png")
            paths = [old_path]

        self.min_confidence = settings.get("min_confidence", 0.55)
        self.min_scale = settings.get("min_scale", 0.50)
        self.max_scale = settings.get("max_scale", 1.60)
        self.scale_step = settings.get("scale_step", 0.05)
        self.min_distance = settings.get("min_distance", 45)
        self.max_detections = settings.get("max_detections", 10)

        self.templates = []

        for index, path in enumerate(paths, start=1):
            template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

            if template is None:
                raise FileNotFoundError(
                    f"Template bulunamadi: {path}"
                )

            self.templates.append((index, template))

    def _match(
        self, frame: np.ndarray, threshold: float
    ) -> List[StoneDetection]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        candidates: List[StoneDetection] = []

        for template_index, template in self.templates:
            template_h, template_w = template.shape

            scale = self.min_scale

            while scale <= self.max_scale + 1e-9:
                width = max(8, int(template_w * scale))
                height = max(8, int(template_h * scale))

                if width <= gray.shape[1] and height <= gray.shape[0]:
                    resized = cv2.resize(
                        template,
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

                    ys, xs = np.where(result >= threshold)

                    for x, y in zip(xs.tolist(), ys.tolist()):
                        candidates.append(
                            StoneDetection(
                                center=(
                                    x + width // 2,
                                    y + height // 2,
                                ),
                                confidence=float(result[y, x]),
                                box=(x, y, width, height),
                                template_index=template_index,
                            )
                        )

                scale += self.scale_step

        return self._remove_duplicates(candidates)

    def detect_all(self, frame: np.ndarray) -> List[StoneDetection]:
        if frame is None or frame.size == 0:
            return []

        detections = self._match(frame, self.min_confidence)
        return detections[: self.max_detections]

    def debug_matches(
        self, frame: np.ndarray, count: int = 15
    ) -> List[StoneDetection]:
        if frame is None or frame.size == 0:
            return []

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


def draw_detection(
    debug: np.ndarray,
    detection: StoneDetection,
    index: int,
    color: Tuple[int, int, int],
) -> None:
    x, y, w, h = detection.box
    cx, cy = detection.center

    cv2.rectangle(debug, (x, y), (x + w, y + h), color, 2)
    cv2.circle(debug, (cx, cy), 5, color, -1)

    label = (
        f"#{index} T{detection.template_index} "
        f"{detection.confidence:.2f}"
    )

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
