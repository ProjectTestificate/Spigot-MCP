#!/usr/bin/python3
import argparse

import platform

import util
import os
import shutil
import subprocess

parser = argparse.ArgumentParser("Decompile the minecraft source")
parser.add_argument('-gradle', help='The directory that gradle is working in', default='gradle-decompile')
parser.add_argument('-template', help='The build.gradle template', default='gradle-decompile/build.gradle.template')
parser.add_argument('-force', '-f', help='Decompile even if the sources have already been decompiled', default=False)
parser.add_argument('out', nargs='?', help='Where to place the output sources', default='decompiled')

args = parser.parse_args()

if platform.python_implementation() == "PyPy":
    print("PyPy is unsupported")
    print("Please use CPython")
    exit(1)

if not os.path.exists(args.template):
    print(args.template, 'doesn\'t exist')
    exit(1)
gradleBuildFile = os.path.join(args.gradle, 'build.gradle')
if os.path.exists(gradleBuildFile):
    print('Deleting', gradleBuildFile)
    os.remove(gradleBuildFile)

print("Generating", gradleBuildFile, 'from', args.template)


if shutil.which("gradle") is None:
    print("Gradle not installed")
    exit(1)

gradleLines = []
buildInfo = util.parse_build_info()
with open(args.template, 'r') as templateFile:
    gradleLines = templateFile.readlines()
gradleLines = buildInfo.rewrite_variables(gradleLines)
with open(gradleBuildFile, "w+") as gradleFile:
    gradleFile.writelines(gradleLines)

# Fake patches dir
util.mkdirs(os.path.join(args.gradle, 'patches'))

gradleDecompiledDir = os.path.join(args.gradle, "projects", "Clean", "src", "main", "java")
if args.force or not os.path.exists(os.path.join(gradleDecompiledDir, "net", "minecraft")):
    print("Tricking ForgeGradle into decompiling minecraft")
    gradle_log = open("gradle.log", "w+")
    result = subprocess.Popen(["gradle", "clean", "setup"], universal_newlines=True,
                                  stdout=gradle_log, stderr=gradle_log, cwd=args.gradle).wait()
    if result != 0:
        print("Unable to decompile minecraft")
        print("See gradle.log for more info")
        exit(1)
    print("Successfully Decompiled minecraft")
else:
    print("Using cached sources")

if os.path.exists(args.out):
    shutil.rmtree(args.out)
shutil.copytree(gradleDecompiledDir, args.out)
print("Decompiled sources put in", args.out)
