import pandas as pd
from pandas.core.frame import DataFrame

dataset = pd.read_parquet('raw-dataset.parquet')

measure_groups = {
    'South America': {
        'providers': {
            'AWS': ['sa-east-1'],
            'AZURE': ['brazilsouth'],
            'GCP': ['southamerica-east1']
        },
        'timezone': 'America/Sao_Paulo'
    },
    'Canada Set': {
        'providers': {
            'AWS': ['ca-central-1'],
            'AZURE': [],
            'GCP': ['northamerica-northeast1']
        },
        'timezone': 'America/Montreal'
    },
    'US Virgina Set': {
        'providers': {
            'AWS': ['us-east-1'],
            'AZURE': ['eastus'],
            'GCP': ['us-east4']
        },
        'timezone': 'America/New_York'
    },
    'UTC 7 Providerset': {
        'providers': {
            'AWS': ['us-west-1', 'us-west-2'],
            'AZURE': ['westus', 'westus2'],
            'GCP': ['us-west2', 'us-west4']
        },
        'timezone': 'America/Los_Angeles'
    },
    'UK Set': {
        'providers': {
            'AWS': ['eu-west-2'],
            'AZURE': ['uksouth'],
            'GCP': ['europe-west2']
        },
        'timezone': 'Europe/London'
    },
    'Germany Set': {
        'providers': {
            'AWS': ['eu-central-1'],
            'AZURE': ['germanywestcentral'],
            'GCP': ['europe-west3']
        },
        'timezone': 'Europe/Berlin'
    },
    'Mumbai Set': {
        'providers': {
            'AWS': ['ap-south-1'],
            'AZURE': ['centralindia'],
            'GCP': ['asia-south1']
        },
        'timezone': 'Asia/Kolkata'
    },
    'Japan Set': {
        'providers': {
            'AWS': ['ap-northeast-1'],
            'AZURE': ['japaneast'],
            'GCP': ['asia-northeast1']
        },
        'timezone': 'Asia/Tokyo'
    },
    'Sydney Set': {
        'providers': {
            'AWS': ['ap-southeast-2'],
            'AZURE': ['australiaeast'],
            'GCP': ['australia-southeast1']
        },
        'timezone': 'Australia/Sydney'
    }
}


# Turn dataset into datetime:
dataset['driver_invocation'] = pd.to_datetime(
    dataset['driver_invocation'], format='%Y%m%dT%H%M%S%f')
dataset['workload_invocation'] = pd.to_datetime(
    dataset['workload_invocation'], format='%Y%m%dT%H%M%S%f')

# Preprocessing based on utc:
dataset['dow_utc'] = dataset['driver_invocation'].dt.day_name()
dataset['tod_utc'] = dataset['driver_invocation'].dt.strftime('%H%M')

print('prepeare local timestamp features')

# Localize Timezones for driver invocation
for mg in measure_groups:
    regions = []
    for provider in measure_groups[mg]['providers']:
        regions.extend(measure_groups[mg]['providers'][provider])

    dataset.loc[(dataset['region'].isin(regions)),
                'timezone'] = measure_groups[mg]['timezone']
    dataset.loc[(dataset['region'].isin(regions)), 'measure group'] = mg

print('local timestamp features')
print(dataset.memory_usage().sum())
dataset[['SAAFMemoryDeltaError', 'SAAFMemoryError', 'vendorId', 'platform', 'payload', 'functionRegion', 'linuxVersion', 'lang', 'functionName', 'cpuType', 'provider',
         'timezone', 'region', 'dow_utc', 'tod_utc', 'measure group']] = dataset[['SAAFMemoryDeltaError', 'SAAFMemoryError', 'vendorId', 'platform', 'payload', 'functionRegion', 'linuxVersion', 'lang', 'functionName', 'cpuType', 'provider',
                                                                                  'timezone', 'region', 'dow_utc', 'tod_utc', 'measure group']].astype('category')

print(dataset.memory_usage().sum())

print(dataset.dtypes)

dataset.to_parquet("dataset-cp1.parquet", index=False, engine="pyarrow")
