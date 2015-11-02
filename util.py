import os
import json
import re
import shutil
import os
import sys
from io import BytesIO
from urllib import request
from zipfile import ZipFile

def mkdirs(dir):
    if os.path.exists(dir): return
    os.makedirs(dir)


def parse_build_info():
    if not os.path.exists("build.json"): raise ValueError("build.json doesn't exist")
    return json.load(open("build.json", "r"), object_hook=BuildInfo)

class BuildInfo:
    VARIABLE_PATTERN = re.compile('\$\{build\.(\w+)\}')

    def __init__(self, data):
        self.minecraftVersion = data["minecraftVersion"]
        self.mappingsVersion = data["mappingsVersion"]

    def rewrite_variables(self, lines):
        def replace(match):
            variableId = match.group(1)
            if variableId == "minecraftVersion": return self.minecraftVersion
            if variableId == "mappingsVersion": return self.mappingsVersion
            raise ValueError("Unknown variable: " + match.group(0))

        newLines = []
        for line in lines:
            line = re.sub(self.VARIABLE_PATTERN, replace, line)
            newLines.append(line)
        return newLines

def include_diffutils():
    try:
        import diffutils
        print("Found diffutils on the path")
        return
    except ImportError:
        # Not found on the path, download
        pass
    output_dir = "DiffUtils"

    download_diffutils(output_dir)

    for file_name in os.listdir(output_dir):
        # Remove all python files in the base dir (setup.py, test.py)
        if file_name.endswith(".py"):
            os.remove(os.path.join(output_dir, file_name))

    sys.path.append(os.path.abspath(output_dir))

DIFFUTILS_URL_PATTERN = "https://github.com/Techcable/DiffUtils/archive/v${version}.zip"
DIFFUTILS_VERSION = "1.0.0"


def download_diffutils(output_dir):
    version_file = os.path.join(output_dir, "version")

    if os.path.exists(version_file) and open(version_file, "r").readline() == DIFFUTILS_VERSION:
        return

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)  # Remove existing files
    mkdirs(output_dir)

    print("Downloading DiffUtils", DIFFUTILS_VERSION)
    url = DIFFUTILS_URL_PATTERN.replace("${version}", DIFFUTILS_VERSION)
    zip_file = ZipFile(BytesIO(request.urlopen(url).read()))  # Python IO

    zip_base_dir = os.path.commonprefix(zip_file.namelist())  # GitHub puts the sources in a directory inside the zip
    if zip_base_dir is '':
        raise ValueError("Invalid zipfile")
    zip_file.extractall(output_dir)

    for file_name in os.listdir(os.path.join(output_dir, zip_base_dir)):
        file = os.path.join(os.path.join(output_dir, zip_base_dir), file_name)
        shutil.move(file, os.path.join(output_dir, file_name))

    os.rmdir(os.path.join(output_dir, zip_base_dir))
    open(version_file, "w+").write(DIFFUTILS_VERSION)


def fix_endings(text):
    if isinstance(text, str):
        return fix_endings([text])[0]

    old_index = 0
    old_size = len(text)
    for original_line in text[:]:
        for line in original_line.splitlines(False):
            line += '\n'
            if old_index < old_size:
                text[old_index] = line
            else:
                text.append(line)
            old_index += 1
