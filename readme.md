
# Description
This script converts Bioshock assets extracted using *Umodel by Gildor* to assets usable by the Half Life: Alyx workshop tools. It uses the *PSK Import addon for Blender by Befzz* to convert the PSKX files to FBX files, the PSKX files to to create VMDL files, the extracted .prop.txt files to create VMAT files as well as copying the proper textures/texture channels and meshes to the mod content folder.

See the following link for a demonstration: https://youtu.be/_TiCz_8QooM

# Requirements:
- Umodel by Gildor:
	- https://www.gildor.org/downloads -> *UE Viewer for Win32*
- python 3.6 or higher
	- https://www.python.org/downloads/
- Python Imaging Library
	- run the command following command from the commandline: ```python3 -m pip install pillow```
- Blender
	- https://www.blender.org/download/
- Blender system PATH variable
	- Windows search -> *Edit the system Enviroment Variables* -> *Enviroment Variables* -> Double click path under *System Variables* -> Paste the installation directory of blender (for example: *C:\Program Files\Blender Foundation\Blender 2.82*) -> Ok..ok..ok
- Blender import PSK addon by Befzz
	- https://github.com/Befzz/blender3d_import_psk_psa
- Installation of Bioshock

# How to use
### Extracting assets:
1. Put the **umodel.exe** and **SDL2.dll** files in the Bioshock root directory (for example: *C:\SteamLibrary\steamapps\common\Bioshock*).
2. Run **umodel.exe**.
3. Click *ok* and wait for the next window to open.
4. In the Package window select *Content->Maps* in the left pane and select from which map you want to export the assets in the right pane. Click *Export*.
4. Check *Use object groups instead of types* and set *Texture format* to *TGA (uncompressed)*. Here you can also set which folder you want to export the assets to. Click *ok* to start the export.

### Converting the assets to Source 2:
1. Download the files of this repository and extract them anywhere.
2. Open a commandline window where you extracted the files and run the following command: ```python3  autoconvert.py "ASSET ROOT" "MOD CONTENT ROOT"``` where **"ASSET ROOT"** is the folder containing assets or subfolders containing the assets (by default this would be *some path/UmodelExport*) and **"MOD CONTENT ROOT"** is the root folder of the content folder of your mod (for example: *G:\SteamLibrary\steamapps\common\Half-Life Alyx\content\hlvr_addons\my_cool_mod*). Both should be enclosed in quotation marks.
3. The source 2 tools will compile the assets when trying to show them in the asset viewer. So looking at all the assets at once in the asset viewer will cause your PC to slow down or the source 2 tools to crash. Either slowley scroll through the assets in the asset browser or simply search for the once you want to use. Once the assets have been compiled, all is dandy.

# Known bugs/Todo:
- automatically figure out wether to use translucency or alpha check
- automatically add hulls to vmdls
- add options to not overwrite existing files (should speed up the whole process when converting the assets of multiple levels, since a lot of assets are duplicated across levels)
- add options to only to part of the conversion (creating vmats, copying textures, creating vmdls, converting meshes)

# Notes:
- When a model seems to kind of show through itself, open the corresponding material and swap translucency for alpha check.
- Add "PhysicsHullFile" and use the mesh fbx and import scale 0.0043 in ModelDoc to add collision to the models.
- Generally tweak the materials of the models to make them look better(for example, play around with metallness and roughness).
