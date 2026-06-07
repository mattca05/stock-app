import subprocess, sys, re

version = sys.argv[1]  # python build.py 1.0.0

# Patch the name in the spec file
with open("StockApp.spec", "r") as f:
    spec = f.read()

spec = re.sub(r"name='StockApp[^']*'", f"name='StockApp-{version}'", spec)

with open("StockApp.spec", "w") as f:
    f.write(spec)

subprocess.run(["pyinstaller", "StockApp.spec"])
