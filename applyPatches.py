import util
import argparse

parser = argparse.ArgumentParser("Generate patches to the MCP sources")
parser.add_argument('-mcp', help='The original mcp sources', default='decompiled')
parser.add_argument('-patches', help='Where to get the patches from', default='patches')
parser.add_argument('src', nargs='?', help='The modified sources', default='src/main/java')

args = parser.parse_args()

util.run_jdiff("--debug", "patch", "--quiet", args.patches, args.mcp, args.src)
