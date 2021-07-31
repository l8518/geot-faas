import json
import subprocess
import os

config_filename = os.getenv('EXPERIMENT_CONFIG') or ""
if config_filename == "":
    raise Exception('Missing Experiment Config')


config = json.load(open(config_filename))

def get_experiment_name():
    return str.lower(f"{config['experiment']['name']}")

def clean_azure(id_core, id, region):
    subprocess.call([f'./clean_azure.sh', id_core, id, region])

def clean_aws(id_core, id, region):
    subprocess.call([f'./clean_aws.sh', id_core, id, region])

def clean_gcp(id_core, id, region):
    subprocess.call([f'./clean_gcp.sh', id_core, id, region])

def clean_core(id_core):
    subprocess.call([f'./clean_core.sh', id_core])

env = get_experiment_name()
id_core = f"{env}core"

for region in config['azure']['regions']:
    print('cleaning azure region', region)
    id = f"{env}{region}"
    clean_azure(id_core, id, region)

for region in config['aws']['regions']:
    id = f"{env}{region}"  
    print('cleaning aws region', region)
    clean_aws(id_core, id, region)

for region in config['gcp']['regions']:
    id = f"{env}{region}" 
    print('cleaning to gcp')
    clean_gcp(id_core, id, region)

clean_core(id_core) # create resources group and arn for saaf
print("all cleaned")