import glob
import multiprocessing
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pandas.core.common import flatten

import pandas as pd
from pandas.core.frame import DataFrame

# Get Experimentname
if len(sys.argv) == 2:
    experimentname = sys.argv[1]
else:
    experimentname = input("Enter experiment name:")

extracted_path = os.path.join("./data/extract/", experimentname)

files = sorted(glob.glob(os.path.join(extracted_path,"*.json")))

def read_into_df(jsonfile):   
    # get filter key (first part of the string to get the different experimental runs)
    key=Path(jsonfile).stem
    filter_key = key[:12]
    folders = glob.glob(os.path.join(extracted_path, f"{filter_key}*{os.path.sep}"))

    # TODO: Raise ERROR IF MORE THAN 29 RESULTS
    if len(folders) != 29:
        print(jsonfile, "WARNING: MORE OR LESS THAN 29 RESULTS FOUND", len(folders))

    dfs = []
    for folder in folders:
        invocation, provider, region = Path(folder).stem.split("_")

        # TODO: Log error somehow:
        file = os.path.join(folder, "saafdemo-basicExperiment-0MBs-run0.csv")
        if os.path.exists(file):
            df = pd.read_csv(file, skiprows=4)
        else:
            df = pd.DataFrame()
            df.insert(0, "error", 'missing csv file')
        
        # Drop last row
        df = df.iloc[:-1 , :]
        df.insert(0, "region", region)
        df.insert(0, "provider", provider)
        df.insert(0, "workload_invocation", invocation)
        df.insert(0, "driver_invocation", key)
        dfs.append(df)
    return pd.concat(dfs)

dataframes = []
with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as tpe:
    dataframes = tpe.map(read_into_df, files)

dataset = pd.concat(list(dataframes))

print('transforming')

dataset = dataset.sort_values(by=['driver_invocation', 'workload_invocation', 'provider', 'region', '1_run_id', '2_thread_id'])
# Make parseable for to_datetime:
dataset['driver_invocation'] = dataset['driver_invocation']+"00"
dataset['workload_invocation'] = dataset['workload_invocation']+"00"

dataset.to_csv('dataset.csv', index=False)

