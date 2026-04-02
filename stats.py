from PIL import Image

img = Image.open("out/png/bar0000.png").convert("RGBA")
a = img.getchannel("A")

mn, mx = a.getextrema()
hist = a.histogram()

print("alpha min:", mn)
print("alpha max:", mx)
print("count alpha=255:", hist[255])
print("count alpha=244:", hist[244])