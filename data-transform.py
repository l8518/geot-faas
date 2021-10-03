import glob
import multiprocessing
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pandas.core.common import flatten
import uuid
from tqdm import tqdm
from datetime import datetime

import pandas as pd
from pandas.core.frame import DataFrame

# Get Experimentname
if len(sys.argv) == 2:
    experimentname = sys.argv[1]
else:
    experimentname = input("Enter experiment name:")

extracted_path = os.path.join("./data/extract/", experimentname)

invocation_files = sorted(glob.glob(os.path.join(extracted_path,"*.json")))
datafolders = sorted(glob.glob(os.path.join(extracted_path,"*[!.json]")))
workers=multiprocessing.cpu_count()

# create week batches:
batches = {}
for invocation_file in invocation_files:
    file_name=Path(invocation_file).stem
    invocation_date = datetime.strptime(file_name[:8], "%Y%m%d")
    cw = invocation_date.isocalendar()[1]
    batch_key = f"{invocation_date.year}-{cw}"
    if batch_key not in batches:
        batches[batch_key] = []
    batches[batch_key].append(invocation_file)


def process_batch(batch_file):
    batch_filename=Path(batch_file).stem
    batch_filter_key = batch_filename[:12]
    pattern = os.path.join(extracted_path, f"{batch_filter_key}")
    folders = list(filter(lambda df: df.startswith(pattern), datafolders))

    dirty_measurement = False
    # TODO: Raise ERROR IF MORE THAN 29 RESULTS
    if len(folders) != 29:
        # print(jsonfile, "WARNING: MORE OR LESS THAN 29 RESULTS FOUND", len(folders))
        dirty_measurement = True
    
    dfs = []
    for folder in folders:
        invocation, provider, region = Path(folder).stem.split("_")
        file = os.path.join(folder, "saafdemo-basicExperiment-0MBs-run0.csv")
        if os.path.exists(file):
            df = pd.read_csv(file, skiprows=4)
            # Drop last row --> contains metadata
            df = df.iloc[:-1 , :]
        else:
            df = pd.DataFrame()
            df.insert(0, "error", 'missing csv file') 

        df.insert(0, "folder_uuid", str(uuid.uuid1()))
        df.insert(0, "dirty_measurement", dirty_measurement)
        df.insert(0, "region", region)
        df.insert(0, "provider", provider)
        df.insert(0, "workload_invocation", invocation)
        df.insert(0, "driver_invocation", batch_filename)
        dfs.append(df)
    return pd.concat(dfs)

# process in batches:
batch_no = 0
for batch, batch_files in batches.items():
    batch_no += 1
    batch_file_length = len(batch_files)
    batch_id = f"{batch}-{batch_file_length}.parquet"
    print(f"Processing batch {batch_id} - {batch_no} of {len(batches)}")

    if os.path.exists(batch_id):
        print('batch already processed, skipping')
        continue 
    
    with ThreadPoolExecutor(max_workers=workers) as tpe:
        batch_frames = list(tqdm(tpe.map(process_batch, batch_files), total=len(batch_files)))
    batch_dataset = pd.concat(list(batch_frames))
    batch_dataset = batch_dataset.sort_values(by=['driver_invocation', 'workload_invocation', 'provider', 'region', '1_run_id', '2_thread_id'])
    batch_dataset.to_parquet(batch_id, engine="pyarrow")

batch_pds = []
for batch, batch_files in batches.items():
    batch_file_length = len(batch_files)
    batch_id = f"{batch}-{batch_file_length}.parquet"
    batch_pds.append(pd.read_parquet(batch_id, engine="pyarrow"))
dataset = pd.concat(batch_pds)

dataset = dataset.sort_values(by=['driver_invocation', 'workload_invocation', 'provider', 'region', '1_run_id', '2_thread_id'])
dataset['driver_invocation'] = dataset['driver_invocation']+"00"
dataset['workload_invocation'] = dataset['workload_invocation']+"00"
dataset.to_parquet("raw-dataset.parquet", index=False, engine="pyarrow")
