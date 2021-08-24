import multiprocessing
import os
import shutil
import sys
import tarfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tqdm import tqdm

# Get Experimentname
if len(sys.argv) == 2:
    experimentname = sys.argv[1]
else:
    experimentname = input("Enter experiment name:")

download_path = os.path.join("./data/downloaded/", experimentname)
tmp_extracted_path = os.path.join("./data/extract/", experimentname)
Path(download_path).mkdir(parents=True, exist_ok=True)
Path(tmp_extracted_path).mkdir(parents=True, exist_ok=True)

# Fetch all files from directory + upload
downloaded_files = sorted(os.listdir(download_path))
extracted_files = sorted(os.listdir(tmp_extracted_path))


def extract(file):
    fp = os.path.join(download_path, file)

    # If JSON File:
    if fp.endswith('.json'):
        if file in extracted_files:
            return

        shutil.copy2(fp, os.path.join(tmp_extracted_path, file))
    else:
        folder_name = file.replace('.tar.gz', '')
        if folder_name in extracted_files:
            return
        try:
            tf = tarfile.open(fp, mode='r:*')
            targetpath = os.path.join(tmp_extracted_path, folder_name)
            tf.extract(tf.getmember(os.path.join('.', 'saafdemo-basicExperiment-0MBs-run0.csv')), targetpath)
            tf.close()
        except Exception as e:
            # TODO: files cannot be found --> extract out or mark as error
            print(e)

result = []
workers = multiprocessing.cpu_count()
with ThreadPoolExecutor(max_workers=workers) as tpe:
    result = list(tqdm(tpe.map(extract, downloaded_files), total=len(downloaded_files)))
