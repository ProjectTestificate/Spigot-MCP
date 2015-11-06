import os
import json
import re
import shutil
import os
import sys
from io import BytesIO
from urllib import request
from zipfile import ZipFile
import subprocess

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

JDIFF_URL = 'https://github.com/Techcable/JDiff/releases/download/v1.0.0/JDiff.jar'
JDIFF_VERSION = "1.0.0"

def get_jdiff():
    version_file = "jdiff-version.txt"
    if os.path.exists(version_file) and open(version_file).read() == JDIFF_VERSION:
        return
    print("Downloading jdiff")
    open("JDiff.jar", "wb+").write(request.urlopen(JDIFF_URL).read())
    open(version_file, "w+").write(JDIFF_VERSION)

def run_jdiff(*args):
    if not shutil.which("java"):
        echo("Java not installed")
        exit(1)
    get_jdiff()
    subprocess.check_call(["java", "-jar", "JDiff.jar"] + list(args), stdout=sys.stdout, stderr=sys.stderr)
