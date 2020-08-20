from sys import argv
from PIL import Image
from pathlib import Path

# APPLYALPHA = False

inFilePath = argv[1]
# inFileName = Path(inFilePath).stem
# outFilePath = Path(r"G:\SteamLibrary\steamapps\common\Half-Life Alyx\content\hlvr_addons\fort_frolic_atrium\materials\textures")
# outFileName = inFileName + "_selfillum.tga"

# print(f"Converting... \n\t{inFileName}.tga")

img = Image.open(inFilePath)
channels = img.split()

# if APPLYALPHA:
# 	bg = Image.new("RGBA", img.size, (0,0,0,255))
# 	bg.paste(img, mask=channels[-1])
# 	bg.save(outFilePath / outFileName)
# else:
# 	channels[1].save(outFilePath / outFileName)

channels[-1].save(Path(r"C:\Users\Mathias\Dropbox\Projects\half life bioshock\autoconvert\temp\test.tga"))
