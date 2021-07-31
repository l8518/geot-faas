import os
from pathlib import Path
import tarfile


log_path = "./data"
tmp_extracted_path = "./data/extracted"

# Fetch all files from directory + upload
for path, subdirs, files in os.walk(log_path):
    print(files)
    for name in files:
        fp = os.path.join(path, name)
        tf=tarfile.open(fp)
        
        targetpath=os.path.join(tmp_extracted_path,name.replace('.tar.gz', ''))
        tf.extractall(targetpath)
        tf.close()
