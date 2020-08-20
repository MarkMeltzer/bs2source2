from pathlib import Path
import shutil
import time
from datetime import datetime
import subprocess
import sys
import pprint
from PIL import Image

asset_root_path = Path(r"G:\SteamLibrary\steamapps\common\Bioshock\UmodelExport\4-Recreation")
mod_content_root_path = Path(r"G:\SteamLibrary\steamapps\common\Half-Life Alyx\content\hlvr_addons\bs_autoconvert_test")

#### SETTINGS ####
LOG_UNDEFINED_DIFFUSE_TEXTURES = False
LOG_UNDEFINED_NORMAL_MAPS = False
LOG_UNDEFINED_OPACITY_MAPS = False

#### get the vmat template ####
with open(r"vmat_template_complex.txt") as f:
    vmat_template = f.read()

#### get the vmdl template ####
with open(r"vmdl_template.txt") as f:
    vmdl_template = f.read()

#### log will contain any missing file errors ####
log = open('logfile.txt', 'a+')
datestring = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
log.write(f"New entry: {datestring}\n")

def parse_proptxt(rawstring):
    lines = rawstring.split("\n")
    
    data_dict = {}
    i = 0
    while lines[i] != "":
        split_line = lines[i].split("=", 1)

        # property = single line
        if split_line[1] != '':
            key = split_line[0][:-1]
            value = split_line[1].strip()

            # property = { single line }
            if value[0] == "{":
                value = {item.split("=")[0] : item.split("=")[1] for item in value[2:-2].split(",")}

            data_dict[key] = value
        else:
            # property = { multiple lines }
            key = lines[i][:-2]
            i += 2 # skip over opening bracket

            bracket_dict = {}
            while lines[i] != "}":
                split_bracket_line = lines[i].split("=")
                bracket_dict[split_bracket_line[0].strip()] = split_bracket_line[1].strip()
                i += 1

            data_dict[key] = bracket_dict
        i += 1
    return data_dict

def vmat_from_proptxt(mat_path, mod_content_root_path):
    start_time = time.time()
    print("\tCreating .vmat file from: ", mat_path.name)

    #### read .mat file ####
    with open(mat_path) as f:
        props_dict = parse_proptxt(f.read())

    #### get names and paths of the texture files ####
    # diffuse texture
    if "Diffuse" in props_dict and props_dict["Diffuse"] != "None":
        diffuse_tga = props_dict["Diffuse"].split(".")[-1][:-1] + ".tga"
        diffuse_tga_path = "materials/textures/" + diffuse_tga
    else:
        # no diffuse texture specified
        diffuse_tga_path = "materials/default/default_color.tga"

        if LOG_UNDEFINED_DIFFUSE_TEXTURES:
            log.write("Diffuse texture not defined in " + mat_path.name + "\n")

    # normal map
    if "NormalMap" in props_dict and props_dict["NormalMap"] != "None":
        normal_tga = props_dict["NormalMap"].split(".")[-1][:-1] + ".tga"
        normal_tga_path = "materials/textures/" + normal_tga
    else:
        # no normal texture specified
        normal_tga_path = "materials/default/default_normal.tga"

        if LOG_UNDEFINED_NORMAL_MAPS:
            log.write("Normal map not defined in " + mat_path.name + "\n")

    # # translucency map
    if "Opacity_Bio" in props_dict and props_dict["Opacity_Bio"]["Material"] != "None":
        trans_tga = props_dict["Opacity_Bio"]["Material"].split(".")[-1][:-1] + ".tga"
        trans_tga_path = "materials/textures/" + trans_tga[:-4] + "_trans.tga"
    else:
        # no opacity texture specified
        trans_tga_path = "materials/default/default_trans.tga"

        if LOG_UNDEFINED_OPACITY_MAPS:
            log.write("Opacity map not defined in " + mat_path.name + "\n")

    #### write to .vmat file ####
    vmat_file_name = mat_path.name[:-10] + ".vmat"
    with open(mod_content_root_path / r"materials" / vmat_file_name, "w") as f:
        vmat = vmat_template.replace("[DIFFUSE TGA PATH]", diffuse_tga_path)
        vmat = vmat.replace("[NORMAL TGA PATH]", normal_tga_path)

        # turn on translucency or not
        if "Opacity_Bio" in props_dict and props_dict["Opacity_Bio"]["Material"] != "None":
            vmat = vmat.replace("[TRANS BOOL INT]", "1")
            vmat = vmat.replace("[TRANS TGA PATH]", trans_tga_path)
        else:
            vmat = vmat.replace("[TRANS BOOL INT]", "0")
        
        f.write(vmat)

    #### copy texture files ####
    try:
        # diffuse texture
        # check if a diffuse texture is specified
        if "Diffuse" in props_dict and props_dict["Diffuse"] != "None":
            if not Path(mat_path.parent / diffuse_tga).is_file():
                # texture is not in the same folder as mat file, go look for it
                found_diffuse_files = list(asset_root_path.glob(r"**/" + diffuse_tga))
                if len(found_diffuse_files) > 0:
                    shutil.copy(found_diffuse_files[0], mod_content_root_path / "materials" / "textures")
                else:
                    log.write("file ", diffuse_tga, " not found in asset root path(or subdirectories)\n")
            else:
                shutil.copy(mat_path.parent / diffuse_tga, mod_content_root_path / "materials" / "textures")

        # normal map
        # check if a normal map is specified
        if "NormalMap" in props_dict and props_dict["NormalMap"] != "None":
            if not Path(mat_path.parent / normal_tga).is_file():
                # texture is not in the same folder as mat file, go look for it
                found_normal_files = list(asset_root_path.glob(r"**/" + normal_tga))
                if len(found_normal_files) > 0:
                    shutil.copy(found_normal_files[0], mod_content_root_path / "materials" / "textures")
                else:
                    log.write("file ", normal_tga, " not found in asset root path(or subdirectories)\n")
            else:
                shutil.copy(mat_path.parent / normal_tga, mod_content_root_path / "materials" / "textures")

        # opacity map
        # check if a opacity map is specified
        if "Opacity_Bio" in props_dict and props_dict["Opacity_Bio"]["Material"] != "None":
            if not Path(mat_path.parent / trans_tga).is_file():
                # texture is not in the same folder as mat file, go look for it
                found_trans_files = list(asset_root_path.glob(r"**/" + trans_tga))
                if len(found_trans_files) > 0:
                    trans_texture_file = found_trans_files[0]
                    channel = int(props_dict["Opacity_Bio"]["Channel"])
                    trans_texture = Image.open(trans_texture_file)
                    trans_texture.split()[channel-1].save(mod_content_root_path / trans_tga_path)
                else:
                    log.write("file ", trans_tga, " not found in asset root path(or subdirectories)\n")
            else:
                channel = int(props_dict["Opacity_Bio"]["Channel"])
                trans_texture = Image.open(mat_path.parent / trans_tga)
                trans_texture.split()[channel-1].save(mod_content_root_path / trans_tga_path)

    except Exception as e:
        log.write(str(e) + "\n")

def vmat_from_mat(mat_path, mod_content_root_path):
    start_time = time.time()
    print("\tCreating .vmat file from: ", mat_path.name)

    #### read .mat file ####
    with open(mat_path) as f:
        mat_file_contents = f.read().split("\n")

    #### get names and paths of the texture files ####
    diffuse_tga = mat_file_contents[0].split("=")[1] + ".tga"
    diffuse_tga_path = "materials/textures/" + diffuse_tga
    if len(mat_file_contents) > 1 and "=" in mat_file_contents[1]:
        normal_tga = mat_file_contents[1].split("=")[1] + ".tga"
        normal_tga_path = "materials/textures/" + normal_tga
    else:
        # no normal map specified
        normal_tga_path = "materials/default/default_normal.tga"

    #### write to .vmat file ####
    vmat_file_name = mat_path.name[:-4] + ".vmat"
    with open(mod_content_root_path / r"materials" / vmat_file_name, "w") as f:
        vmat = vmat_template.replace("[DIFFUSE TGA PATH]", diffuse_tga_path)
        vmat = vmat.replace("[NORMAL TGA PATH]", normal_tga_path)
        f.write(vmat)

    #### copy texture files ####
    try:
        # diffuse texture
        if not Path(mat_path.parent / diffuse_tga).is_file():
            # texture is not in the same folder as mat file, go look for it
            found_diffuse_files = list(asset_root_path.glob(r"**/" + diffuse_tga))
            if len(found_diffuse_files) > 0:
                shutil.copy(found_diffuse_files[0], mod_content_root_path / "materials" / "textures")
            else:
                log.write("file ", diffuse_tga, " not found in asset root path(or subdirectories)\n")
        else:
            shutil.copy(mat_path.parent / diffuse_tga, mod_content_root_path / "materials" / "textures")

        # normal map
        if len(mat_file_contents) > 1 and "=" in mat_file_contents[1]:
            # check if a normal map is specified
            if not Path(mat_path.parent / normal_tga).is_file():
                # texture is not in the same folder as mat file, go look for it
                found_normal_files = list(asset_root_path.glob(r"**/" + normal_tga))
                if len(found_normal_files) > 0:
                    shutil.copy(found_normal_files[0], mod_content_root_path / "materials" / "textures")
                else:
                    log.write("file ", normal_tga, " not found in asset root path(or subdirectories)\n")
            else:
                shutil.copy(mat_path.parent / normal_tga, mod_content_root_path / "materials" / "textures")
    except Exception as e:
        log.write(str(e) + "\n")

def get_materials_from_pskx(filename):
    #### read the file in binary ####
    with open(filename, "rb") as f:
        contents = f.read()

    #### find roughly the start of where the materials are listed ####
    start_i = contents.find(b"MATT0000") + len("MATT0000")

    materials = []
    material = ""
    non_char_series = True
    for i in range(start_i, len(contents)):
        char = contents[i]
        
        # check for material name characters
        if char > 32 and char < 127:
            non_char_series = False
            material += chr(char)
        elif not non_char_series:
            # this marks the end of the material list
            if material == "REFSKELT":
                break

            # we are coming out of a character sequence
            non_char_series = True

            materials.append(material)
            material = ""

    # ignore the first 3 letters
    return materials[3:]

def vmdl_from_pskx(pskx_path, mod_content_root_path):
    print("\tCreating .vmdl file from: ", pskx_path.name)

    #### getting the materials from the pskx/psk file ####
    materials = get_materials_from_pskx(pskx_path)

    #### create materials nodes for .vmdl file ####
    material_nodes = ""
    for material in materials:
        material_nodes += (f"{{\n\t\t\t\t\t\t\t\tfrom = \"{material}.vmat\"\n"
                          f"\t\t\t\t\t\t\t\tto = \"materials/{material}.vmat\"\n\t\t\t\t\t\t\t}},")

    #### write to .vmat file ####
    vmdl_file_name = pskx_path.name.split(".")[0] + ".vmdl"
    with open(mod_content_root_path / r"models" / vmdl_file_name, "w") as f:
        vmdl = vmdl_template.replace("[MATERIALS]", material_nodes)
        vmdl = vmdl.replace("[MESHFILE PATH]", "\"models/meshes/" + pskx_path.name.split(".")[0] + ".fbx\"")
        f.write(vmdl)

total_start_time = time.time()

print("Creating vmats.....")
start_time = time.time()
n = 0
for f in asset_root_path.glob(r"**/*"):
    if f.suffix == ".txt":
        n += 1
        vmat_from_proptxt(f, mod_content_root_path)
print(f"Created {n} vmats in {time.time() - start_time:.3f} seconds")

print("Creating vmdls.....")
start_time = time.time()
n = 0
for f in asset_root_path.glob(r"**/*"):
    if f.suffix == ".pskx" or f.suffix == ".psk":
        n += 1
        vmdl_from_pskx(f, mod_content_root_path)
print(f"Created {n} vmdls in {time.time() - start_time:.3f} seconds")

print("Converting pskxs to fbxs.....")
subprocess.call(["blender", "-b", "-P", "pskx_to_fbx.py", "--", asset_root_path, 
                mod_content_root_path / "models" / "meshes"],
                stdout=subprocess.DEVNULL, stderr=sys.stdout)

print(f"Total runtime: {time.time() - total_start_time:.3f} seconds")

log.write("\n")
log.close()