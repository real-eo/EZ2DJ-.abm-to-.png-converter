from PIL import Image
from constants import DIRECTORY
import os



IMG_PATH = r"C:\Users\reale\OneDrive - Akademiet Norge AS\VS code\Python\EZ2CATCH abm to png\out\ez2catch\panel\Catcher4\4bar0000.png"
BAR_WIDTH = 60
SHOW_ZERO_ROWS = False                                                                  # True = print all 256 alpha values, False = only values that occur

imgPath = os.path.join(DIRECTORY.OUTPUT, IMG_PATH)
img = Image.open(imgPath).convert("RGBA")
a = img.getchannel("A")

mn, mx = a.getextrema()
hist = a.histogram()                                                                    # 256 bins for alpha channel

print(f"image: {imgPath}")
print(f"alpha min: {mn}")
print(f"alpha max: {mx}")
print()


top5 = sorted(
    ((value, count) for value, count in enumerate(hist) if count > 0),
    key=lambda x: x[1],
    reverse=True,
)[:5]
for rank, (value, count) in enumerate(top5, start=1):
    print(f"#{rank} alpha count ({value:>3}): {count}")

print()

maxCount = max(hist) if hist else 1

if maxCount == 0:
    maxCount = 1

print("alpha histogram (ASCII):")
print("value |  count  | graph")
print("-" * 90)

for value, count in enumerate(hist):
    if not SHOW_ZERO_ROWS and count == 0:
        continue

    barLength = int((count / maxCount) * BAR_WIDTH) if count > 0 else 0
    bar = "#" * barLength
    print(f"{value:>5} | {count:>7} | {bar}")
