from parse import ABMFile, ABMMask
from constants import DIRECTORY
from PIL import Image
import os


def convert(abmPath: str, maskPath: str, outputPath=f"output.png", normalizeAlpha=True):
    # Normalize resource path in-place
    if (not os.path.isabs(abmPath)
    and not os.path.normpath(abmPath).startswith(os.path.normpath(DIRECTORY.RESOURCES) + os.sep)):
        abmPath = os.path.join(DIRECTORY.RESOURCES, abmPath)

    if (not os.path.isabs(maskPath)
    and not os.path.normpath(maskPath).startswith(os.path.normpath(DIRECTORY.RESOURCES) + os.sep)):
        maskPath = os.path.join(DIRECTORY.RESOURCES, maskPath)


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



# TODO: I know this algorithm has some glaring flaws, but i cba to fix it rn
def _isSingleExtraM(spriteStem: str, maskStem: str) -> bool:
    return (
        spriteStem.count("m") == maskStem.count("m") - 1
        and len(maskStem) == len(spriteStem) + 1
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


def dirConvert(dirPath: str, outputDir=DIRECTORY.OUTPUT, normalizeAlpha=True):
    baseDir = dirPath if os.path.isabs(dirPath) else os.path.join(DIRECTORY.RESOURCES, dirPath)

    for root, _, files in os.walk(baseDir):
        abmFiles = [f for f in files if f.endswith(".abm")]
        fileSet = set(abmFiles)

        # First pass: resolve the selected mask for each sprite filename.
        selectedMasks = {
            file: _resolveMaskForSprite(file, fileSet)
            for file in abmFiles
        }

        # Second pass: only skip files that are actually used as masks for another sprite.
        usedAsMask = {
            mask for sprite, mask in selectedMasks.items() if mask != sprite
        }

        for file in abmFiles:
            if file in usedAsMask:
                continue

            abmPath = os.path.join(root, file)
            maskFile = selectedMasks[file]
            maskPath = os.path.join(root, maskFile)

            relativePath = os.path.relpath(abmPath, DIRECTORY.RESOURCES)
            outputPath = os.path.join(outputDir, os.path.splitext(relativePath)[0] + ".png")

            convert(abmPath, maskPath, outputPath, normalizeAlpha=normalizeAlpha)



# * Usage
# Converts all sprite ABM files under the folder and uses a paired mask when present.
dirConvert("ez2catch/panel/Catcher1")
dirConvert("ez2catch/panel/Catcher2")
# dirConvert("ez2catch/panel/note/strawberry/common")
convert("ez2catch/panel/note/strawberry/note_1.abm", 
        "ez2catch/panel/note/strawberry/note_1.abm", 
        "ez2catch/panel/note/strawberry/note_1.png"
)
