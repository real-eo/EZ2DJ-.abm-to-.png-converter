from src.parse import ABMFile, ABMMask
from src.constants import DIRECTORY
from pathlib import Path
from PIL import Image
import os


def convert(abmPath: (Path | str), maskPath: (Path | str), outputPath: (Path | str)=Path("output.png"), normalizeAlpha=True):
    print(f"Converting: {abmPath}")
    print(f"Using mask: {maskPath}")

    # Convert to Path objects if not already, for easier path manipulations
    abmPath     = abmPath       if isinstance(abmPath, Path)    else Path(abmPath)
    maskPath    = maskPath      if isinstance(maskPath, Path)   else Path(maskPath)
    outputPath  = outputPath    if isinstance(outputPath, Path) else Path(outputPath)

    # Normalize resource path in-place
    if not abmPath.is_absolute():
        try:                abmPath.relative_to(DIRECTORY.RESOURCES)
        except ValueError:  abmPath = DIRECTORY.RESOURCES / abmPath

    if not maskPath.is_absolute():
        try:                maskPath.relative_to(DIRECTORY.RESOURCES)
        except ValueError:  maskPath = DIRECTORY.RESOURCES / maskPath


    # Read the file as bytes, and decode pairs of 3 bytes to RGB values.
    abmFile = ABMFile(abmPath)
    maskFile = ABMMask(
        maskPath, 
        normalize=normalizeAlpha, 
        invert=(abmPath != maskPath)                                                    # Invert if not the same file, since self-masking sprites use opposite convention
    )

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
    try:
        alpha = Image.frombytes(
            maskFile.COLOR_MODE,
            (maskFile.width, maskFile.height),
            maskFile.maskData,
            "raw",
            maskFile.COLOR_FORMAT,
        ).transpose(Image.FLIP_TOP_BOTTOM)

    # If mask is not present, create a fully opaque alpha channel
    except TypeError:   alpha = Image.new("L", (abmFile.width, abmFile.height), 255)

    img.putalpha(alpha)
    

    # Normalize output path in-place
    if not outputPath.is_absolute():                                                    # If outputPath is not an absolute path, save to output directory
        try:                outputPath.relative_to(DIRECTORY.OUTPUT)
        except ValueError:  outputPath = DIRECTORY.OUTPUT / outputPath
    
    # Save    
    outputPath.parent.mkdir(parents=True, exist_ok=True)                                # Ensure output directory exists
    img.save(outputPath)
    
    print(f"  Saved to: {outputPath}\n")



# TODO: I know this algorithm has some glaring flaws, but i cba to fix it rn
def _isSingleExtraM(spriteStem: str, maskStem: str) -> bool:
    return (
        spriteStem.count("m") == (maskStem.count("m") - 1)
        and len(maskStem) == (len(spriteStem) + 1)
        and sum(map(ord, maskStem)) - sum(map(ord, spriteStem)) == ord("m")
    )


def _resolveMaskForSprite(spriteFilename: str, fileSet: set[str]) -> str:
    spriteStem, spriteExt = os.path.splitext(spriteFilename)

    for candidate in sorted(fileSet):
        if candidate == spriteFilename:                 continue

        candidateStem, candidateExt = os.path.splitext(candidate)
        if candidateExt.lower() != spriteExt.lower():   continue

        if _isSingleExtraM(spriteStem, candidateStem):  return candidate

    return spriteFilename


def dirConvert(dirPath: (Path | str), outputDir: (Path | str)=DIRECTORY.OUTPUT, normalizeAlpha=True):
    # Convert to Path objects if not already
    dirPath     = dirPath   if isinstance(dirPath, Path)    else Path(dirPath)
    outputDir   = outputDir if isinstance(outputDir, Path)  else Path(outputDir)

    # Normalize paths in-place
    baseDir     = dirPath   if dirPath.is_absolute()        else DIRECTORY.RESOURCES / dirPath

    # Collect unique directories containing ABM files
    for folder in sorted({p.parent for p in baseDir.rglob("*.abm")}):
        abmNames = [p.name for p in sorted(folder.glob("*.abm"))]
        fileSet = set(abmNames)

        # First pass: resolve the selected mask for each sprite filename.
        selectedMasks = {
            name: _resolveMaskForSprite(name, fileSet)
            for name in abmNames
        }

        # Second pass: only skip files that are actually used as masks for another sprite.
        usedAsMask = {
            mask for sprite, mask in selectedMasks.items() if mask != sprite
        }

        # Final pass: convert each ABM file with its selected mask (which may be itself if no better match was found).
        for name in abmNames:
            if name in usedAsMask:
                continue

            abmPath     = folder / name
            maskPath    = folder / selectedMasks[name]
            outputPath  = outputDir / abmPath.relative_to(DIRECTORY.RESOURCES).with_suffix(".png")

            convert(abmPath, maskPath, outputPath, normalizeAlpha=normalizeAlpha)
        



# * Usage
# Converts all sprite ABM files under the folder and uses a paired mask when present.
dirConvert("ez2catch")
# dirConvert("ez2catch/panel/Catcher1")
# dirConvert("ez2catch/panel/Catcher2")
# dirConvert("ez2catch/panel/Catcher3")
# dirConvert("ez2catch/panel/Catcher4")
# dirConvert("ez2catch/panel/Catcher5")
# dirConvert("ez2catch/panel/Catcher6")
# dirConvert("ez2catch/panel/Catcher7")
# dirConvert("ez2catch/panel/note/strawberry/common")
# convert("ez2catch/panel/note/strawberry/note_1.abm", 
#         "ez2catch/panel/note/strawberry/note_1.abm", 
#         "ez2catch/panel/note/strawberry/note_1.png"
# )
