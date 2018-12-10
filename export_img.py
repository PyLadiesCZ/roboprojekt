import sys
import subprocess
from pathlib import Path

base = Path(".")

inkscape = "C:/Program Files/Inkscape/inkscape"
def prevod_svg_png():
    for soubor in base.glob("*.svg"):
        jmeno = str(soubor)
        nove_jmeno = jmeno[:-4] + ".png"
        subprocess.run([inkscape, jmeno, "--export-png=" + nove_jmeno, "--export-area-page"],check = True,)

prevod_svg_png()
print("Done")
