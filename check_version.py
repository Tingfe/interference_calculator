#!/usr/bin/env python3
import subprocess
import sys

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

print("=== Git Log (last 5 commits) ===")
print(run_cmd("git log --oneline -5"))

print("\n=== Current HEAD commit ===")
print(run_cmd("git rev-parse HEAD"))

print("\n=== v2.6.0 tag commit ===")
print(run_cmd("git rev-parse v2.6.0 2>/dev/null || echo 'Tag not found'"))

print("\n=== __version__ in __init__.py ===")
with open("interference_calculator/__init__.py", "r") as f:
    for line in f:
        if "__version__" in line and "=" in line:
            print(line.strip())
            break

print("\n=== Remote tags on origin ===")
print(run_cmd("git ls-remote --tags origin | grep v2.6.0"))
