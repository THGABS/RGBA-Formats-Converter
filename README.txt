Version : 0.5 (07/02/2025)

To run the .py (source) version, you'll need :
- to have python 3.6 or more
- the Pillow (PIL fork) library
it should work on both windows and linux.
otherwise if you're on windows you can directly use
the .exe released on github.

When you have all of this, simply run the MAIN.py file.

Changelog :
0.5 (07/02/2025)
  - Add the preset "Bedrock MERS to labPBR 1.3"
  - Add a feature to replace one keyword to another in converted files
  - Now checkboxes will be automatically disabled when they do not work
  - Colors of controls are now determined by class variables (the palette) instead of being assigned for each control
0.4 (10/11/2020)
  - fixed a bug where it would not detect file outside of propage mode
  - checked options so that by default it's setup to convert a whole mc ressource pack
0.3 (09/09/2020)
  - you can now choose source and target folder with the "..." buttons
  - A warning box is displayed when the conversion finish successfully
  - docstrings have been added to the convert() and convert_img() methods
0.2 (27/07/2020)
  - fix presets
  - improved perf
  - sub-folder propagation is now an option (works only when overwrite is enabled)
  - removed some print
  - improved feedback a bit
0.1 (04/07/2020)
  - This thing now exist
