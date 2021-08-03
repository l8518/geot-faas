import os
import sys
import tarfile
import shutil
from pathlib import Path
import glob
import pandas as pd

# Get Experimentname
if len(sys.argv) == 2:
    experimentname = sys.argv[1]
else:
    experimentname = input("Enter experiment name:")

extracted_path = os.path.join("./data/extract/", experimentname)

dataframes = []
for jsonfile in sorted(glob.glob(os.path.join(extracted_path,"*.json"))):
    print(jsonfile)
    # get filter key (first part of the string to get the different experimental runs)
    key=Path(jsonfile).stem
    filter_key = key[:12]
    folders = glob.glob(os.path.join(extracted_path, f"{filter_key}*{os.path.sep}"))

    # TODO: Raise ERROR IF MORE THAN 29 RESULTS
    if len(folders) != 29:
        print("WARNING: MORE OR LESS THAN 29 RESULTS FOUND", len(folders))

    for folder in folders:
        invocation, provider, region = Path(folder).stem.split("_")

        df = pd.read_csv(os.path.join(folder, "saafdemo-basicExperiment-0MBs-run0.csv"), skiprows=4)
        # Drop last row
        df = df.iloc[:-1 , :]
        df.insert(0, "region", region)
        df.insert(0, "provider", provider)
        df.insert(0, "workload_invocation", invocation)
        df.insert(0, "driver_invocation", key)
        dataframes.append(df)

dataset = pd.concat(dataframes)


dataset = dataset.sort_values(by=['driver_invocation', 'workload_invocation', 'provider', 'region', '1_run_id', '2_thread_id'])
# Make parseable for to_datetime:
dataset['driver_invocation'] = dataset['driver_invocation']+"00"
dataset['workload_invocation'] = dataset['workload_invocation']+"00"

dataset.to_csv('dataset.csv', index=False)

