import cv2

IMAGE = "metin2_test.png"
OUTPUTS = [
    "stone_template_1.png",
    "stone_template_2.png",
    "stone_template_3.png",
]

image = cv2.imread(IMAGE)

if image is None:
    print("metin2_test.png bulunamadi.")
    raise SystemExit

print("3 farkli Metin tasindan template olusturacagiz.")
print("Her pencerede tasi tamamen kapsayan bir dikdortgen sec.")
print("ENTER = onayla, ESC = iptal et.")
print()

for index, output in enumerate(OUTPUTS, start=1):
    print(f"[{index}/3] Metin tasini sec: {output}")

    x, y, w, h = cv2.selectROI(
        f"Metin Tasi {index}",
        image,
        showCrosshair=True,
        fromCenter=False,
    )

    cv2.destroyAllWindows()

    if w == 0 or h == 0:
        print("Secim yapilmadi. Islem durduruldu.")
        raise SystemExit

    template = image[y:y + h, x:x + w]

    if cv2.imwrite(output, template):
        print(f"Kaydedildi: {output}")
    else:
        print(f"Kaydedilemedi: {output}")
        raise SystemExit

print()
print("3 template hazir.")
