import pandas as pd

dataset = pd.read_parquet('dataset-preprocessing-step-2.parquet')


print(dataset.memory_usage().sum())