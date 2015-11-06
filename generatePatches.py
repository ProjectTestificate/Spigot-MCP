import util
import argparse

parser = argparse.ArgumentParser("Generate patches to the MCP sources")
parser.add_argument('-mcp', help='The original mcp sources', default='decompiled')
parser.add_argument('-out', help='Where to place the generated patches', default='patches')
parser.add_argument('src', nargs='?', help='The modified sources', default='src/main/java')

args = parser.parse_args()

util.run_jdiff("--debug", "diff", "--parallel", "--quiet", args.mcp, args.src, args.out)
