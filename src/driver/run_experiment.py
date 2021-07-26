import json
import subprocess
import concurrent.futures
import os

num_launcher=8
config = json.load(open('/scripts/deploy_config.json'))


def get_experiment_name():
    experiment_env = os.getenv('EXPERIMENT_ENV') or ""
    return str.lower(f"{config['experiment']['name']}{experiment_env}")

def run_azure(id, region):
    cp = subprocess.call([f'/scripts/run_azure.sh', id, region])
    # TODO: Log the errors if they occur here
    print(cp)

def run_aws(id, region):
    cp = subprocess.call([f'/scripts/run_aws.sh', id, region])
    # TODO: Log the errors if they occur here
    print(cp)

def run_gcp(id, region):
    cp = subprocess.call([f'/scripts/run_gcp.sh', id, region])
    # TODO: Log the errors if they occur here
    print(cp)

def measure_azure(region):
    env = get_experiment_name()
    id = f"{env}{region}"
    print(f'measuring azure {id}')
    run_azure(id, region)

def measure_aws(region):
    env = get_experiment_name()
    id = f"{env}{region}"
    print(f'measuring aws {id}')
    run_aws(id, region)

def measure_gcp(region):
    env = get_experiment_name()
    id = f"{env}{region}"
    print(f'measuring gcp {id}')
    run_gcp(id, region)

executor = concurrent.futures.ProcessPoolExecutor(num_launcher)
futures_azure = [executor.submit(measure_azure, region) for region in config['azure']['regions']]
futures_aws = [executor.submit(measure_aws, region) for region in config['aws']['regions']]
futures_gcp = [executor.submit(measure_gcp, region) for region in config['gcp']['regions']]

fts = concurrent.futures.wait(futures_aws + futures_azure + futures_gcp)
print(fts)
