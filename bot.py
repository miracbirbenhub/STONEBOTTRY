from vision.screen import Screen
from vision.detector import StoneDetector
from config import BOT_CONFIG

import cv2


def main():
    print("STONEBOTTRY - visual detection debug")
    print("Ekran taraniyor...")

    screen = Screen()
    detector = StoneDetector(BOT_CONFIG["detection"])

    frame = screen.capture_game_region()
    if frame is None:
        print("Ekran yakalanamadi.")
        return

    result = detector.detect(frame)
    debug = frame.copy()

    if result.found:
        x, y = result.center
        h, w = detector.template_gray.shape

        left = max(0, x - w // 2)
        top = max(0, y - h // 2)
        right = min(debug.shape[1], x + w // 2)
        bottom = min(debug.shape[0], y + h // 2)

        cv2.rectangle(debug, (left, top), (right, bottom), (0, 0, 255), 3)
        cv2.circle(debug, (x, y), 6, (0, 255, 0), -1)

        label = f"Stone: ({x}, {y})  Confidence: {result.confidence:.2f}"
        cv2.putText(
            debug,
            label,
            (max(10, left), max(30, top - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        print(f"Found coordinate: ({x}, {y})")
        print(f"Confidence: {result.confidence:.2f}")
    else:
        print(f"No stone found. Best confidence: {result.confidence:.2f}")
        cv2.putText(
            debug,
            "No stone detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )

    cv2.imwrite("debug_detection.png", debug)

    print("Debug image saved: debug_detection.png")
    print("Press any key in the image window to close.")

    cv2.imshow("STONEBOTTRY - Detection", debug)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
