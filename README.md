# EZ2DJ-.abm-to-.png-converter
This program converts `.abm` files used in the EZ2DJ/EZ2AC series into `.png` with alpha channel when supplied with a `.abm` mask file

## Usage
For now the program is just used manually via python, as i don't want to sink too much time into a proper interface. It should be pretty straight forward once you have the required libraries installed (Pillow)

### Step 1
Place all `.abm` files with the `res/` folder.

### Step 2
Configure `opaque.py` and `alpha.py` to your preference by programming in either `convert(...)` or `dirConvert(...)` commands below the `# * Usage` comment in either files. P.S: There are some pre-existing examples already present in both files. 

> [!NOTE]
> `opaque.py` converts `.abm` into non-transparent images, while `alpha.py` converts into RGBA, but requires a mask to do so. Often, these masks are found along sprites, but in some cases, the sprites themselves are masks. In that case, just use the same path for both sprite and mask.

### Step 3
Run the configured scripts (`opaque.py` and `alpha.py`). There should be no runtime errors unless you've forgotten to comment out the examples i left, or if you've wrongfully tried to use either command.

#### Notice
> [!NOTE]
> Both absolute and relative paths can be used, but know that when using relative paths for either input or output, they get put in their respective folder. See `res/README.md` and `out/README.md` for like 10% more info.
