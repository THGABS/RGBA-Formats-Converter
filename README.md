# RGBA Formats Converter
To run the `.py` (source) version, you need:
- To have [Python](https://python.org) 3.6 or higher
- The [Pillow](https://github.com/python-pillow/Pillow) (PIL fork) library
It should work on both Windows and Linux.

When you have all of this, simply run the `MAIN.py` file.

## Changelog
### 0.6 (07/07/2025)
  - Fixed an issue where Keyword Replace feature does not work
  - Now conversion is allowed to propagate to subfolders without overwriting the original files
  - The program is now able to create output folders if they do not exist
  - Now it's possible to convert and output single one image, not only preview it
  - Corrected typos in the original code
  - Made UI labels easier to understand
  - Cleaned up the code and unified expressions of image list generation
### 0.5 (07/02/2025)
  - Add the preset "Bedrock MERS to labPBR 1.3"
  - Add a feature to replace one keyword to another in converted files
  - Now checkboxes will be automatically disabled when they do not work
  - Colors of controls are now determined by class variables (the palette), instead of being assigned for each control
    - Now it uses the same palette as Ore UI! 
  - An info box will be displayed when it's converted successfully, instead of a warning box
  - Set the default windows size
### 0.4 (10/11/2020)
  - fixed a bug where it would not detect file outside of propagetion mode
  - checked options so that by default it's set up to convert a whole mc resource pack
### 0.3 (09/09/2020)
  - you can now choose source and target folder with the "..." buttons
  - A warning box is displayed when the conversion finish successfully
  - docstrings have been added to the `convert()` and `convert_img()` methods
### 0.2 (27/07/2020)
  - fix presets
  - improved perf
  - sub-folder propagation is now an option (works only when overwrite is enabled)
  - removed some print
  - improved feedback a bit
### 0.1 (04/07/2020)
  - This thing now exists
