from parse import ABMFile
from constants import DIRECTORY
from PIL import Image
import os

def convert(abmPath: str, outputPath=f"output.png"):    
    # Normalize resource path in-place
    if (not os.path.isabs(abmPath)
    and not os.path.normpath(abmPath).startswith(os.path.normpath(DIRECTORY.RESOURCES) + os.sep)):
        abmPath = os.path.join(DIRECTORY.RESOURCES, abmPath)

    
    # Read the file as bytes, and decode pairs of 3 bytes to RGB values.
    abmFile = ABMFile(abmPath)


    # | DEBUG: Print some info about the ABM file
    # | print(f"\nABM file: {abmPath}")
    # | print(f"Width: {abmFile.width}")
    # | print(f"Height: {abmFile.height}")
    # | print(f"Color Mode: {abmFile.COLOR_MODE}")
    # | print(f"Color Format: {abmFile.COLOR_FORMAT}")
    # | print(f"Pixel data length: {len(abmFile.pixelData)} bytes")
    # | print("First 10 pixels (BGR):")
    # | for i in range(min(10, len(abmFile.pixelData) // 3)):
    # |     b, g, r = abmFile.pixelData[i*3:(i+1)*3]
    # |     print(f"  Pixel {i}: B={b}, G={g}, R={r}")

    # Create image
    img = Image.frombytes(
        abmFile.COLOR_MODE,                                                             # Color mode (3 bytes per pixel)
        (abmFile.width, abmFile.height),                                                # Image dimensions
        abmFile.pixelData,                                                              # Data
        "raw",                                                                          # Raw data, no compression
        abmFile.COLOR_FORMAT,                                                           # Color format (BGR in this case; not RGB)
    ).transpose(Image.FLIP_TOP_BOTTOM)                                                  # ABM images are stored upside-down      


    # Normalize output path in-place
    if (not os.path.isabs(outputPath)                                                   # If outputPath is not an absolute path, save to output directory
    and not os.path.normpath(outputPath).startswith(os.path.normpath(DIRECTORY.OUTPUT) + os.sep)):
        outputPath = os.path.join(DIRECTORY.OUTPUT, outputPath)

    # Save    
    os.makedirs(os.path.dirname(outputPath), exist_ok=True)                             # Ensure output directory exists
    img.save(outputPath)
    
    # | if abmFile.padded:
    # |     print(f"Saved to {outputPath}")

    print(f"Saved to {outputPath}")


# Convert all ABM files in a directory and subdirectories to PNG, maintaining the directory structure in the output directory.
def dirConvert(dirPath, outputDir=DIRECTORY.OUTPUT):
    baseDir = dirPath if os.path.isabs(dirPath) else os.path.join(DIRECTORY.RESOURCES, dirPath)

    for root, _, files in os.walk(baseDir):
        for file in files:
            if file.endswith(".abm"):
                abmPath = os.path.join(root, file)

                # Keep full path under res/ in output
                relativePath = os.path.relpath(abmPath, DIRECTORY.RESOURCES)

                outputPath = os.path.join(outputDir, os.path.splitext(relativePath)[0] + ".png")
                convert(abmPath, outputPath)


# * Usage
# dirConvert("ez2catch/panel/")
dirConvert("ez2catch/panel/Catcher4/")