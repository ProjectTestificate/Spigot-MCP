#!/usr/bin/env python3
import util
import os
import argparse

util.include_diffutils()
import diffutils

parser = argparse.ArgumentParser("Generate patches to the MCP sources")
parser.add_argument('-mcp', help='The original mcp sources', default='decompiled')
parser.add_argument('-out', help='Where to place the generated patches', default='patches')
parser.add_argument('src', nargs='?', help='The modified sources', default='src/main/java')

args = parser.parse_args()

for dir, subDirs, files in os.walk(args.mcp):
    for file in files:
        file = os.path.join(dir, file)
        relative = os.path.relpath(file, args.mcp)
        modifiedFile = os.path.join(args.src, relative)
        if not os.path.exists(modifiedFile): continue
        output = os.path.join(args.out, relative + ".patch")
        util.mkdirs(os.path.dirname(output))

        original_lines = open(file).readlines()
        new_lines = open(modifiedFile).readlines()

        patch = diffutils.diff(original_lines, new_lines)
        if patch is None: continue
        diff_lines = diffutils.generate_unified_diff("a/" + relative.replace("\\", "/"), "b/" + relative.replace("\\", "/"), original_lines, patch, 3)
        print("Writing generated patch", output)

        util.fix_endings(diff_lines)
        open(output, "w+").writelines(diff_lines)
