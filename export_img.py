"""
Inkscape needs to be installed.
Run the file from the root directory of the project.
Program export all images in SVG format to PNG format in directories/subdirectories.
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
    Check if inkscape is installed and can be run
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
    Export images in SVG format to PNG format with Inkscape
    """
    # Choose images in directories/subdirectories with SVG suffix
    # https://github.com/pyvec/pyworking-materials/blob/master/180617_Soubory_barvy/pathlib.ipynb
    for img in Path("./img").glob("**/*.svg"):
        name = str(img)
        parts = []
        for part in img.with_suffix(".png").parts:
            if part == "svg":
                parts.append("png")
            else:
                parts.append(part)
        # variable number of arguments, '*' inserts list elements as function arguments
        # https://github.com/frenzymadness/Advanced_PyLadies/blob/master/03_functions_arguments/functions_arguments.ipynb
        new_name = Path(*parts)
        # create parent directory
        new_name.parent.mkdir(exist_ok=True, parents=True)
        # launch Inkscape and export all images to PNG format
        # https://docs.python.org/3/library/subprocess.html
        subprocess.run([inkscape, name, "--export-png=" + str(new_name), "--export-area-page"], check=True)

export_svg_png()
print("Done")
