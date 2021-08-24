import pandas as pd
from multiprocessing import  Pool
import multiprocessing

from functools import partial
import numpy as np

dataset = pd.read_parquet('dataset-cp1.parquet')


def get_local_dow_of_the_week(df):
    ts = df['driver_invocation']
    tz = df['timezone']
    return  ts.tz_localize('utc').tz_convert(tz).day_name()


def get_local_tod_of_the_week(df):
    ts = df['driver_invocation']
    tz = df['timezone']
    return ts.tz_localize('utc').tz_convert(tz).strftime('%H%M')

def parallelize(data, func, num_of_processes=8):
    data_split = np.array_split(data, num_of_processes)
    pool = Pool(num_of_processes)
    data = pd.concat(pool.map(func, data_split))
    pool.close()
    pool.join()
    return data

def run_on_subset(func, data_subset):
    return data_subset.apply(func, axis=1)

def parallelize_on_rows(data, func):
    return parallelize(data, partial(run_on_subset, func), multiprocessing.cpu_count())

print(dataset.memory_usage().sum())

dataset['local_dow'] = parallelize_on_rows(dataset[['driver_invocation', 'timezone']], get_local_dow_of_the_week) 
dataset['local_tod'] = parallelize_on_rows(dataset[['driver_invocation', 'timezone']], get_local_tod_of_the_week) 

print(dataset.memory_usage().sum())

dataset[['local_dow', 'local_tod']] = dataset[['local_dow', 'local_tod']].astype('category')

print(dataset.memory_usage().sum())

dataset.to_parquet("dataset.parquet", index=False, engine="pyarrow")
