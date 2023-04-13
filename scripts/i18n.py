import os
import sys

from glob import glob
from subprocess import call

if __name__ == "__main__":
    try:
        type_ = sys.argv[1]
        lang_ = sys.argv[2]
    except:
        print("Missing arguments. Expected: (generate|edit|release) <LANG_CODE>.")
        sys.exit(1)
    
    if type_ == "generate":
        files = glob(os.path.join(".", "src", "**", "*.py"), recursive = True)
        call([
            "pylupdate6",
            "--verbose",
            *files,
            "-ts",
            os.path.join(".", "src", "res", "translations", f"{lang_}.ts")
        ], shell = True)
    elif type_ == "edit":
        print(os.path.join(".", ".venv", "Lib", "site-packages", "qt6_applications", "Qt", "bin", "linguist.exe"))
        call([
            os.path.join(".", "venv", "Lib", "site-packages", "qt6_applications", "Qt", "bin", "linguist.exe"),
            os.path.join(".", "src", "res", "translations", f"{lang_}.ts")
        ], shell = True)
    elif type_ == "release":
        call([
            os.path.join(".", "venv", "Lib", "site-packages", "qt6_applications", "Qt", "bin", "lrelease.exe"),
            os.path.join(".", "src", "res", "translations", f"{lang_}.ts")
        ], shell = True)
    else:
        print("Invalid arguments. Expected: (generate|edit|release) <LANG_CODE>.")
        sys.exit(1)