import json
import subprocess
import os

config_filename = os.getenv('EXPERIMENT_CONFIG') or ""
if config_filename == "":
    raise Exception('Missing Experiment Config')

config = json.load(open(config_filename))

def get_experiment_name():
    return str.lower(f"{config['experiment']['name']}")

env = get_experiment_name()
id_core = f"{env}core"

for pr in config['experiment-provider-locations']:

    provider = pr['provider']
    region = pr['region']
    # shorten id because azure only accepts max 24 chars
    id = f"{env}{region}"[:24]

    print(f'cleaning {provider} region {region}')
    if provider == 'azure':
        subprocess.call([f'./clean_azure.sh', id_core, id, region])
    elif provider == 'aws':
        subprocess.call([f'./clean_aws.sh', id_core, id, region])
    elif provider == 'gcp':
        subprocess.call([f'./clean_gcp.sh', id_core, id, region])
    else:
        raise Exception('Unknown Provider')

subprocess.call([f'./clean_core.sh', id_core])
print("all cleaned")