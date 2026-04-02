from PIL import Image
from constants import DIRECTORY
import os



IMG_PATH = "png/bar0000.png"
BAR_WIDTH = 60
SHOW_ZERO_ROWS = False                                                                  # True = print all 256 alpha values, False = only values that occur

imgPath = os.path.join(DIRECTORY.OUTPUT, IMG_PATH)
img = Image.open(imgPath).convert("RGBA")
a = img.getchannel("A")

mn, mx = a.getextrema()
hist = a.histogram() # 256 bins for alpha channel

print(f"image: {imgPath}")
print(f"alpha min: {mn}")
print(f"alpha max: {mx}")
print(f"count alpha=255: {hist[255]}")
print(f"count alpha=244: {hist[244]}")
print()

max_count = max(hist) if hist else 1

if max_count == 0:
    max_count = 1

print("alpha histogram (ASCII):")
print("value | count | graph")
print("-" * 90)

for value, count in enumerate(hist):
    if not SHOW_ZERO_ROWS and count == 0:
        continue

    bar_len = int((count / max_count) * BAR_WIDTH) if count > 0 else 0
    bar = "#" * bar_len
    print(f"{value:>5} | {count:>7} | {bar}")
