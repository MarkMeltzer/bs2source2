import bpy
import io_import_scene_unreal_psa_psk_280 as imp
import sys
from pathlib import Path
import time

argv = sys.argv[sys.argv.index("--") + 1:]
if len(argv) != 2:
    print("Usage: \n blender -b -P pskx_to_fbx.py -- [pskx/psk folder source path] [fbx destination path]")

pskx_folder = Path(argv[0])
start_time = time.time()
n = 0
for f in pskx_folder.glob(r"**/*"):
    if f.suffix == ".pskx" or f.suffix == ".psk":
        print(f"\tConverting: {f.name}", file=sys.stderr)

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        ctxt = bpy.context
        imp.pskimport(str(f), context=ctxt)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.fbx(filepath=str(Path(argv[1]) / (f.name.split(".")[0] + ".fbx")))

        n +=1
print(f"Converted {n} models in {time.time() - start_time:.3f} seconds", file=sys.stderr)