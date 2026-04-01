from PIL import Image
from parse import ABMFile, MaskFile
from constants import DIRECTORY


def convert(abmPath, maskPath, outputPath=f"output.png", normalizeAlpha=False):
    # Read the file as bytes, and decode pairs of 3 bytes to RGB values.
    abmFile = ABMFile(abmPath if ":" in abmPath else f"{DIRECTORY.RESOURCES}/{abmPath}")
    maskFile = MaskFile(maskPath if ":" in maskPath else f"{DIRECTORY.RESOURCES}/{maskPath}", normalize=normalizeAlpha)

    # Ensure dimensions match
    if (abmFile.width, abmFile.height) != (maskFile.width, maskFile.height):
        raise ValueError("ABM and mask dimensions do not match")

    # Create image
    img = Image.frombytes(
        abmFile.COLOR_MODE,                                                             # Color mode (3 bytes per pixel)
        (abmFile.width, abmFile.height),                                                # Image dimensions
        abmFile.pixelData,                                                              # Data
        "raw",                                                                          # Raw data, no compression
        abmFile.COLOR_FORMAT,                                                           # Color format (BGR in this case; not RGB)
        # ? Moved to separate lines for clarity:
        # // 0,                                                                              # Stride (0: calculate based on width and color format)
        # // -1,                                                                             # Orientation (-1: image is stored upside-down)
    ).transpose(Image.FLIP_TOP_BOTTOM)                                                  # ABM images are stored upside-down                             

    # Add data to alpha channel
    alpha = Image.frombytes(
        maskFile.COLOR_MODE,
        (maskFile.width, maskFile.height),
        maskFile.maskData,
        "raw",
        maskFile.COLOR_FORMAT,
    ).transpose(Image.FLIP_TOP_BOTTOM)    

    img.putalpha(alpha)
    
    # Save
    if ("\\" not in outputPath) or ("/" not in outputPath):  
        outputPath = f"{DIRECTORY.OUTPUT}/{outputPath}"
    
    img.save(outputPath)
    
    print(f"Saved to {outputPath}")



# Usage
convert("2bar0000.abm", "2barm0000.abm", "tangle.png", normalizeAlpha=True)