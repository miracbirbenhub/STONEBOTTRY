from vision.screen import Screen
from vision.detector import StoneDetector, draw_detection
from config import BOT_CONFIG

import cv2


def _is_near_existing(detection, existing, distance=45):
    x, y = detection.center
    for item in existing:
        ex, ey = item.center
        if ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5 < distance:
            return True
    return False


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
    debug_matches = detector.debug_matches(frame, count=15)
    debug = frame.copy()

    print()
    print(f"Normal esik: {detector.min_confidence:.2f}")

    if detections:
        print(f"Esigi gecen aday sayisi: {len(detections)}")
        print()

        for index, detection in enumerate(detections, start=1):
            x, y = detection.center

            print(
                f"  METIN #{index}: "
                f"X={x}, Y={y} | "
                f"Confidence={detection.confidence:.3f} | "
                f"Template={detection.template_index}"
            )

            # Green = accepted Metin candidate.
            draw_detection(debug, detection, index, (0, 255, 0))

            # Put a larger coordinate label near the center so it remains
            # readable even when the detection box is small.
            cv2.putText(
                debug,
                f"METIN #{index}  X:{x} Y:{y}",
                (max(10, x - 100), min(debug.shape[0] - 10, y + 45)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
    else:
        print("Normal esigi gecen Metin tasi yok.")

    print()
    print("En guclu dusuk-esik eslesmeleri:")

    debug_index = 1

    for detection in debug_matches:
        # Do not draw low-threshold debug boxes over accepted detections.
        if _is_near_existing(detection, detections):
            continue

        print(
            f"  DEBUG #{debug_index}: "
            f"X={detection.center[0]}, Y={detection.center[1]} | "
            f"Confidence={detection.confidence:.3f}"
        )

        draw_detection(debug, detection, debug_index, (0, 180, 255))
        debug_index += 1

    cv2.imwrite("debug_detection.png", debug)

    print()
    print("Debug goruntusu: debug_detection.png")
    print("YESIL = kabul edilen Metin tasi")
    print("SARI = sadece dusuk-esik debug adayi")
    print("=" * 50)

    cv2.imshow("STONEBOTTRY - Template Debug", debug)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
