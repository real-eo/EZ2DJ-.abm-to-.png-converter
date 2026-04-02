from constants import DIRECTORY
from PIL import Image
from PIL import ImageOps
import os


def convert(imagePath: str, maskPath: str, outputPath="output.png", normalizeAlpha=True, invertMask=True):
    # Normalize resource path in-place
    if (not os.path.isabs(imagePath)
    and not os.path.normpath(imagePath).startswith(os.path.normpath(DIRECTORY.RESOURCES) + os.sep)):
        imagePath = os.path.join(DIRECTORY.RESOURCES, imagePath)

    if (not os.path.isabs(maskPath)
    and not os.path.normpath(maskPath).startswith(os.path.normpath(DIRECTORY.RESOURCES) + os.sep)):
        maskPath = os.path.join(DIRECTORY.RESOURCES, maskPath)

    # Load color image and grayscale mask from separate PNG files.
    img = Image.open(imagePath).convert("RGBA")
    alpha = Image.open(maskPath).convert("L")

    if img.size != alpha.size:
        raise ValueError("Image and mask dimensions do not match")

    if normalizeAlpha:
        # Normalize the alpha values to the range [0, 255]
        minVal = min(alpha.getdata())
        maxVal = max(alpha.getdata())

        if maxVal > minVal:
            alpha = alpha.point(lambda p: (p - minVal) * 255 // (maxVal - minVal))

    if invertMask:
        alpha = ImageOps.invert(alpha)

    img.putalpha(alpha)
    
    # Normalize output path in-place
    if (not os.path.isabs(outputPath)                                                   # If outputPath is not an absolute path, save to output directory
    and not os.path.normpath(outputPath).startswith(os.path.normpath(DIRECTORY.OUTPUT) + os.sep)):
        outputPath = os.path.join(DIRECTORY.OUTPUT, outputPath)

    # Save
    outputDirname = os.path.dirname(outputPath)
    if outputDirname:
        os.makedirs(outputDirname, exist_ok=True)
    img.save(outputPath)
    
    print(f"Saved to {outputPath}")


def dirConvert(spriteDir: str, maskDir: str, outputDir=DIRECTORY.OUTPUT, normalizeAlpha=True, invertMask=True):
    spriteBase = spriteDir if os.path.isabs(spriteDir) else os.path.join(DIRECTORY.RESOURCES, spriteDir)
    maskBase = maskDir if os.path.isabs(maskDir) else os.path.join(DIRECTORY.RESOURCES, maskDir)

    for root, _, files in os.walk(spriteBase):
        pngFiles = [f for f in files if f.lower().endswith(".png")]

        for file in pngFiles:
            imagePath = os.path.join(root, file)
            relativePath = os.path.relpath(imagePath, spriteBase)
            maskPath = os.path.join(maskBase, relativePath)

            if not os.path.exists(maskPath):
                print(f"Skipping {imagePath}: missing mask {maskPath}")
                continue

            outputPath = os.path.join(outputDir, os.path.splitext(relativePath)[0] + ".png")
            convert(imagePath, maskPath, outputPath, normalizeAlpha=normalizeAlpha, invertMask=invertMask)



# * Usage
# Example usage with explicit sprite and mask directories.
# dirConvert("ez2catch/panel/Catcher1", "ez2catch/panel/Catcher1_mask")
# convert("ez2catch/panel/Catcher1/1.png", "ez2catch/panel/Catcher1_mask/1.png", "out/1.png")
convert("png/bar0000.png", "png/barm0000.png", "png/bar0000.png")
