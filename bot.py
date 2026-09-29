from time import monotonic, sleep

import cv2

from config import BOT_CONFIG
from input.controller import InputController
from vision.detector import StoneDetector, StoneDetection
from vision.screen import Screen


def choose_target(detections: list[StoneDetection], frame_width: int, frame_height: int):
    """Choose the accepted stone closest to the game viewport center."""
    if not detections:
        return None

    cx = frame_width / 2
    cy = frame_height / 2
    bias = BOT_CONFIG["targeting"].get("center_bias", 0.15)

    def score(detection):
        x, y = detection.center
        dx = (x - cx) / max(1, frame_width)
        dy = (y - cy) / max(1, frame_height)
        distance = (dx * dx + dy * dy) ** 0.5
        return distance - detection.confidence * bias

    return min(detections, key=score)


def main():
    print("STONEBOTTRY - AUTO TARGET")
    print("=" * 50)
    print("Normal kullanici seviyesi mouse ile hedef secimi aktif.")
    print("Durdurmak icin CTRL+C kullan.")

    screen = Screen()
    detector = StoneDetector(BOT_CONFIG["detection"])
    controller = InputController()
    targeting = BOT_CONFIG["targeting"]

    last_click = 0.0

    while True:
        frame = screen.capture_game_region()
        if frame is None:
            print("Ekran yakalanamadi.")
            sleep(1.0)
            continue

        detections = detector.detect_all(frame)
        target = choose_target(detections, frame.shape[1], frame.shape[0])

        if target is None:
            print("Metin bulunamadi; yeniden taraniyor...")
            sleep(targeting["rescan_delay"])
            continue

        now = monotonic()
        if now - last_click < targeting["click_delay"]:
            sleep(0.05)
            continue

        x, y = target.center
        print(
            f"HEDEF -> X={x}, Y={y} | "
            f"Confidence={target.confidence:.3f} | "
            f"Template={target.template_index}"
        )

        controller.click_at(x, y)
        last_click = now
        sleep(targeting["rescan_delay"])


if __name__ == "__main__":
    main()
