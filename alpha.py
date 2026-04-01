from parse import ABMFile, MaskFile
from constants import DIRECTORY
from PIL import Image
import os


def convert(abmPath: str, maskPath: str, outputPath=f"output.png", normalizeAlpha=False):
    # Normalize resource path in-place
    if (not os.path.isabs(abmPath)
    and not os.path.normpath(abmPath).startswith(os.path.normpath(DIRECTORY.RESOURCES) + os.sep)):
        abmPath = os.path.join(DIRECTORY.RESOURCES, abmPath)

    if (not os.path.isabs(maskPath)
    and not os.path.normpath(maskPath).startswith(os.path.normpath(DIRECTORY.RESOURCES) + os.sep)):
        maskPath = os.path.join(DIRECTORY.RESOURCES, maskPath)


    # Read the file as bytes, and decode pairs of 3 bytes to RGB values.
    abmFile = ABMFile(abmPath)
    maskFile = MaskFile(maskPath, normalize=normalizeAlpha)


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
    
    # Normalize output path in-place
    if (not os.path.isabs(outputPath)                                                   # If outputPath is not an absolute path, save to output directory
    and not os.path.normpath(outputPath).startswith(os.path.normpath(DIRECTORY.OUTPUT) + os.sep)):
        outputPath = os.path.join(DIRECTORY.OUTPUT, outputPath)

    # Save    
    os.makedirs(os.path.dirname(outputPath), exist_ok=True)                             # Ensure output directory exists
    img.save(outputPath)
    
    print(f"Saved to {outputPath}")



# * Usage
# All files in: "ez2catch\panel\note\strawberry\common"

# All files in: "ez2catch\panel\Catcher1"
convert("ez2catch/panel/Catcher1/bar0000.abm", "ez2catch/panel/Catcher1/barm0000.abm", "catcher1-0.png", normalizeAlpha=True)
convert("ez2catch/panel/Catcher1/bar0001.abm", "ez2catch/panel/Catcher1/barm0001.abm", "catcher1-1.png", normalizeAlpha=True)

# All files in: "ez2catch\panel\Catcher2"
convert("ez2catch/panel/Catcher2/2bar0000.abm", "ez2catch/panel/Catcher2/2barm0000.abm", "catcher2-0.png", normalizeAlpha=True)
convert("ez2catch/panel/Catcher2/2bar0001.abm", "ez2catch/panel/Catcher2/2barm0001.abm", "catcher2-1.png", normalizeAlpha=True)
