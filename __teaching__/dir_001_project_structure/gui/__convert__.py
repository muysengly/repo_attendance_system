import os
import glob

for file in glob.glob("**/*.ui"):
    print(f"{file}")
    os.system(f"pyuic5 -x {file} -o {file[:-3]}.py")
