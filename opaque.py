from src.constants import DIRECTORY
from src.parse import ABMFile
from pathlib import Path
from PIL import Image
import os

def convert(abmPath: (Path | str), outputPath=Path("output.png")):
    print(f"Converting: {abmPath}")

    # Convert to Path objects if not already, for easier path manipulations
    abmPath     = Path(abmPath)     if not isinstance(abmPath, Path)    else abmPath
    outputPath  = Path(outputPath)  if not isinstance(outputPath, Path) else outputPath


    # Normalize resource path in-place
    if not abmPath.is_absolute():
        try:                abmPath.relative_to(DIRECTORY.RESOURCES)
        except ValueError:  abmPath = DIRECTORY.RESOURCES / abmPath

    
    # Read the file as bytes, and decode pairs of 3 bytes to RGB values.
    abmFile = ABMFile(abmPath)

    # Create image
    img = Image.frombytes(
        abmFile.COLOR_MODE,                                                             # Color mode (3 bytes per pixel)
        (abmFile.width, abmFile.height),                                                # Image dimensions
        abmFile.pixelData,                                                              # Data
        "raw",                                                                          # Raw data, no compression
        abmFile.COLOR_FORMAT,                                                           # Color format (BGR in this case; not RGB)
    ).transpose(Image.FLIP_TOP_BOTTOM)                                                  # ABM images are stored upside-down      


    # Normalize output path in-place
    if not outputPath.is_absolute():
        try:                outputPath.relative_to(DIRECTORY.OUTPUT)
        except ValueError:  outputPath = DIRECTORY.OUTPUT / outputPath

    # Save    
    outputPath.parent.mkdir(parents=True, exist_ok=True)                                # Ensure output directory exists
    img.save(outputPath)
    
    print(f"  Saved to: {outputPath}\n")



# Convert all ABM files in a directory and subdirectories to PNG, maintaining the directory structure in the output directory.
def dirConvert(dirPath: (Path | str), outputDir: (Path | str)=DIRECTORY.OUTPUT):
    # Convert to Path objects if not already, for easier path manipulations
    dirPath    = dirPath    if isinstance(dirPath, Path)    else Path(dirPath)
    outputDir  = outputDir  if isinstance(outputDir, Path)  else Path(outputDir)

    # Normalize paths in-place
    baseDir     = dirPath   if dirPath.is_absolute()        else DIRECTORY.RESOURCES / dirPath


    # Walk through all ABM files in the directory and subdirectories
    for abmPath in baseDir.rglob("*.abm"):
        # Keep full path under res/ in output
        relativePath = abmPath.relative_to(DIRECTORY.RESOURCES)
        outputPath = outputDir / relativePath.with_suffix(".png")
        convert(abmPath, outputPath)


# * Usage
dirConvert("ez2catch/panel/")
# dirConvert("ez2catch/panel/Catcher3/")