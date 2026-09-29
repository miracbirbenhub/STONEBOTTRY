from vision.screen import Screen
from vision.detector import StoneDetector
from config import BOT_CONFIG

import cv2


def main():
    print("STONEBOTTRY - MULTI STONE DETECTION")
    print("=" * 50)

    screen = Screen()
    detector = StoneDetector(BOT_CONFIG["detection"])

    frame = screen.capture_game_region()

    if frame is None:
        print("Ekran yakalanamadi.")
        return

    detections = detector.detect_all(frame)
    debug = frame.copy()

    print()

    if not detections:
        print("Hicbir Metin tasi bulunamadi.")
        cv2.putText(
            debug,
            "NO STONES DETECTED",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )
    else:
        print(f"{len(detections)} adet aday Metin tasi bulundu.")
        print()

        for index, detection in enumerate(detections, start=1):
            x, y = detection.center
            box_x, box_y, width, height = detection.box

            print(
                f"{index}. X={x}, Y={y} | "
                f"Confidence={detection.confidence:.2f}"
            )

            cv2.rectangle(
                debug,
                (box_x, box_y),
                (box_x + width, box_y + height),
                (0, 0, 255),
                3,
            )

            cv2.circle(
                debug,
                (x, y),
                7,
                (0, 255, 0),
                -1,
            )

            label = (
                f"#{index} ({x}, {y}) "
                f"{detection.confidence:.2f}"
            )

            cv2.putText(
                debug,
                label,
                (box_x, max(30, box_y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

    cv2.imwrite("debug_detection.png", debug)

    print()
    print("Debug goruntusu: debug_detection.png")
    print("=" * 50)
    print("Goruntu penceresini kapatmak icin bir tusa basin.")

    cv2.imshow("STONEBOTTRY - Multi Stone Detection", debug)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
