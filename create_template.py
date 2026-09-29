import cv2

IMAGE = "metin2_test.png"
OUTPUT = "stone_template.png"

image = cv2.imread(IMAGE)

if image is None:
    print("metin2_test.png bulunamadi.")
    raise SystemExit

print("Metin tasinin etrafini mouse ile sec.")
print("Secim bitince ENTER'a bas.")
print("Iptal etmek icin ESC'ye bas.")

x, y, w, h = cv2.selectROI(
    "Metin Tasi Sec",
    image,
    showCrosshair=True,
    fromCenter=False
)

cv2.destroyAllWindows()

if w == 0 or h == 0:
    print("Secim yapilmadi.")
    raise SystemExit

template = image[y:y+h, x:x+w]

if cv2.imwrite(OUTPUT, template):
    print(f"Template kaydedildi: {OUTPUT}")
else:
    print("Template kaydedilemedi.")