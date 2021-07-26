import os
from pathlib import Path
import tarfile




log_path = "./data"
tmp_extracted_path = "./tmp/data"

def extract():
    # Fetch all files from directory + upload
    for path, subdirs, files in os.walk(log_path):
        print(files)
        for name in files:
            fp = os.path.join(path, name)
            tf=tarfile.open(fp)
            
            targetpath=os.path.join(tmp_extracted_path,name.replace('.tar.gz', ''))
            tf.extractall(targetpath)
            tf.close()

extract()

# my_tar = tarfile.open('my_tar.tar.gz')
# my_tar.extractall('./my_folder') # specify which folder to extract to
# my_tar.close()