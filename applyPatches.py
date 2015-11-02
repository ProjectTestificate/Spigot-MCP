#!/usr/bin/python3
import argparse
import os
import util

util.include_diffutils()
import diffutils

parser = argparse.ArgumentParser("Apply patches to the MCP sources")
parser.add_argument('-mcp', help='The original mcp sources', default='decompiled')
parser.add_argument('-patches', help='Where to get the patches from', default='patches')
parser.add_argument('src', nargs='?', help='The modified sources', default='src/main/java')

args = parser.parse_args()

for dir, subDirs, files in os.walk(args.patches):
    for file in files:
        file = os.path.join(dir, file)
        relative = os.path.relpath(file, args.patches)
        relative = relative[:relative.rfind('.')]  # Remove the '.patch'

        diff_lines = open(file).readlines()
        patch = diffutils.parse_unified_diff(diff_lines)

        print("Patching", relative, "with", file)

        original = os.path.join(args.mcp, relative)
        original_lines = open(original).readlines()

        new_lines = diffutils.patch(original_lines, patch)
        util.fix_endings(new_lines)

        output = os.path.join(args.src, relative)
        util.mkdirs(os.path.dirname(output))
        open(output, "w+").writelines(new_lines)
