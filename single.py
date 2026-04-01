from PIL import Image
from parse import ABMFile


def convert(abmLocation, outputFile="output.png"):
    # Read the file as bytes, and decode pairs of 3 bytes to RGB values.
    abmFile = ABMFile(abmLocation)

    # Create image
    img = Image.frombytes(
        "RGB",                                                                          # Color mode (3 bytes per pixel)
        (abmFile.width, abmFile.height),                                                # Image dimensions
        abmFile.pixelData,                                                              # Data
        "raw",                                                                          # Raw data, no compression
        abmFile.COLOR_FORMAT,                                                           # Color format (BGR in this case; not RGB)
        # ? Moved to separate lines for clarity:
        # // 0,                                                                              # Stride (0: calculate based on width and color format)
        # // -1,                                                                             # Orientation (-1: image is stored upside-down)
    )

    # Some formats are stored upside-down
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    img.save(outputFile)
    print(f"Saved to {outputFile}")


# Usage
convert("2bar0000.abm", "output.png")
# convert("score_2.abm", "output.png")