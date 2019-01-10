"""
Program export images in SVG format to PNG format.
Open file in directory where you have svg images saved.
"""
import subprocess
from pathlib import Path

inkscape_paths = [
    "inkscape",
    "C:/Program Files/Inkscape/inkscape",
    "C:/Program Files (x86)/Inkscape/inkscape"
    ]

def run_inkscape(path):
    """
    Check if inscape path run Inscape
    """
    try:
        subprocess.run([path, "--version"],
                       stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def find_inkscape_path():
    """
    Return first functional Inkscape path
    """
    for path in inkscape_paths:
        if run_inkscape(path):
            return path

inkscape = find_inkscape_path()

def export_svg_png():
    """
    Export img.svg to img.png with Inkscape
    """
    for img in Path("./img").glob("**/*.svg"):
        name = str(img)
        parts = []
        for part in img.with_suffix(".png").parts:
            if part == "svg":
                parts.append("png")
            else:
                parts.append(part)
            new_name = Path(*parts)
        Path(*parts).parent.mkdir(exist_ok = True, parents= True)
        subprocess.run([inkscape, name, "--export-png=" + str(new_name), "--export-area-page"], check = True,)

export_svg_png()
print("Done")
