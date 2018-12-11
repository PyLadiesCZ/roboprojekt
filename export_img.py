"""
Program for exporting images in svg format to png format.

Open file in directory where you have svg images saved.
First update inkscape path, where you have inscape installed on your computer - 'inkscape'
"""
import sys
import subprocess
from pathlib import Path

base = Path(".") #current directory where are svg images

inkscape = "C:/Program Files/Inkscape/inkscape" #update
def prevod_svg_png():
    for soubor in base.glob("*.svg"):
        jmeno = str(soubor)
        nove_jmeno = jmeno[:-4] + ".png"
        subprocess.run([inkscape, jmeno, "--export-png=" + nove_jmeno, "--export-area-page"],check = True,)

prevod_svg_png()
print("Done")
