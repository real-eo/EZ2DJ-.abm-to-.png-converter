from src.constants import DIRECTORY
from pathlib import Path
from PIL import ImageOps
from PIL import Image
import os


def convert(imagePath: (Path | str), maskPath: (Path | str), outputPath: (Path | str)=Path("output.png"), normalizeAlpha=True, invertMask=True):
    # Convert to Path objects if not already, for easier path manipulations
    imagePath   = Path(imagePath)   if not isinstance(imagePath, Path)  else imagePath
    maskPath    = Path(maskPath)    if not isinstance(maskPath, Path)   else maskPath
    outputPath  = Path(outputPath)  if not isinstance(outputPath, Path) else outputPath

    # Normalize resource path in-place
    if not imagePath.is_absolute():
        try:                imagePath.relative_to(DIRECTORY.RESOURCES)
        except ValueError:  imagePath = DIRECTORY.RESOURCES / imagePath

    if not maskPath.is_absolute():
        try:                maskPath.relative_to(DIRECTORY.RESOURCES)
        except ValueError:  maskPath = DIRECTORY.RESOURCES / maskPath

    # Load color image and grayscale mask from separate PNG files.
    img: Image.Image = Image.open(imagePath).convert("RGBA")
    alpha: Image.Image = Image.open(maskPath).convert("L")

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
    if not outputPath.is_absolute():                                                    # If outputPath is not an absolute path, save to output directory
        try:                outputPath.relative_to(DIRECTORY.OUTPUT)
        except ValueError:  outputPath = DIRECTORY.OUTPUT / outputPath

    # Save
    outputPath.parent.mkdir(parents=True, exist_ok=True)
    img.save(outputPath)
    
    print(f"Saved to {outputPath}")


def dirConvert(spriteDir: (Path | str), maskDir: (Path | str), outputDir: (Path | str)=DIRECTORY.OUTPUT, normalizeAlpha=True, invertMask=True):
    # Convert to Path objects
    spriteDir   = spriteDir if isinstance(spriteDir, Path)  else Path(spriteDir)
    maskDir     = maskDir   if isinstance(maskDir, Path)    else Path(maskDir)
    outputDir   = outputDir if isinstance(outputDir, Path)  else Path(outputDir)

    # Normalize paths in-place
    spriteBase  = spriteDir if spriteDir.is_absolute() else DIRECTORY.RESOURCES / spriteDir
    maskBase    = maskDir   if maskDir.is_absolute()   else DIRECTORY.RESOURCES / maskDir

    # Walk through all PNG files in the sprite directory, find corresponding mask files, and convert them.
    for imagePath in spriteBase.rglob("*.png"):
        relativePath = imagePath.relative_to(spriteBase)
        maskPath = maskBase / relativePath

        if not maskPath.exists():
            print(f"Skipping {imagePath}: missing mask {maskPath}")
            continue

        outputPath = (outputDir / relativePath).with_suffix(".png")
        convert(
            imagePath,
            maskPath,
            outputPath,
            normalizeAlpha=normalizeAlpha,
            invertMask=invertMask,
        )



# * Usage
# Example usage with explicit sprite and mask directories.
# dirConvert("ez2catch/panel/Catcher1", "ez2catch/panel/Catcher1_mask")
# convert("ez2catch/panel/Catcher1/1.png", "ez2catch/panel/Catcher1_mask/1.png", "out/1.png")
convert("png/bar0000.png", "png/barm0000.png", "png/bar0000.png")
