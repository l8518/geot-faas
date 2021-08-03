import os
import sys
import tarfile
import shutil
from pathlib import Path

# Get Experimentname
if len(sys.argv) == 2:
    experimentname = sys.argv[1]
else:
    experimentname = input("Enter experiment name:")

download_path = os.path.join("./data/downloaded/", experimentname)
tmp_extracted_path = os.path.join("./data/extract/", experimentname)
Path(download_path).mkdir(parents=True, exist_ok=True)

# Fetch all files from directory + upload
for path, subdirs, files in os.walk(download_path):
    for name in files:
        fp = os.path.join(path, name)


        # If JSON File:
        if fp.endswith('.json'):
            shutil.copy2(fp, os.path.join(tmp_extracted_path, name))
        else:
            tf = tarfile.open(fp)

            targetpath = os.path.join(
                tmp_extracted_path, name.replace('.tar.gz', ''))
            tf.extractall(targetpath)
            tf.close()
