from vision.screen import Screen
from vision.detector import StoneDetector
from config import BOT_CONFIG

def main():
    print("STONEBOTTRY Python prototype")
    print("Metin2 window capture/detection test starting...")

    screen = Screen()
    detector = StoneDetector(BOT_CONFIG["detection"])

    frame = screen.capture_game_region()
    if frame is None:
        print("Could not capture the configured region.")
        return

    result = detector.detect(frame)
    if result.found:
        print(f"Possible Metin stone detected at screen coordinates: {result.center}")
        print(f"Confidence: {result.confidence:.2f}")
    else:
        print("No stone detected in the current frame.")
        print("Next step: add a real stone template from your client.")

if __name__ == "__main__":
    main()
