from vision.screen import Screen
from vision.detector import StoneDetector, draw_detection
from config import BOT_CONFIG

import cv2


def main():
    print("STONEBOTTRY - TEMPLATE DEBUG")
    print("=" * 50)

    screen = Screen()
    detector = StoneDetector(BOT_CONFIG["detection"])

    frame = screen.capture_game_region()

    if frame is None:
        print("Ekran yakalanamadi.")
        return

    detections = detector.detect_all(frame)
    debug_matches = detector.debug_matches(frame, count=10)
    debug = frame.copy()

    print()
    print(f"Normal esik: {detector.min_confidence:.2f}")

    if detections:
        print(f"Esigi gecen aday sayisi: {len(detections)}")
        for index, detection in enumerate(detections, start=1):
            print(
                f"  GERCEK ADAY #{index}: "
                f"X={detection.center[0]}, Y={detection.center[1]} | "
                f"Confidence={detection.confidence:.3f}"
            )
            draw_detection(debug, detection, index, (0, 255, 0))
    else:
        print("Normal esigi gecen Metin tasi yok.")

    print()
    print("En guclu dusuk-esik eslesmeleri:")

    for index, detection in enumerate(debug_matches, start=1):
        print(
            f"  #{index}: "
            f"X={detection.center[0]}, Y={detection.center[1]} | "
            f"Confidence={detection.confidence:.3f}"
        )

        # Yellow/orange-style debug boxes mark candidates only.
        draw_detection(debug, detection, index, (0, 180, 255))

    if not debug_matches:
        print("Hic eslesme uretilemedi.")

    cv2.imwrite("debug_detection.png", debug)

    print()
    print("Debug goruntusu: debug_detection.png")
    print("Yesil = normal esigi gecen aday")
    print("Turuncu = sadece debug icin dusuk esik adayi")
    print("=" * 50)

    cv2.imshow("STONEBOTTRY - Template Debug", debug)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
