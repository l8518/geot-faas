import concurrent.futures
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from azure.storage.blob import BlobServiceClient

num_launcher = 8
log_path = '/tmp/invocations/'
config = json.load(open('/scripts/deploy_config.json'))

def upload_file(fp, name, azure_connecting_string, container):
    blob_service_client = BlobServiceClient.from_connection_string(azure_connecting_string)
    with open(fp, "rb") as data:
        blob_client = blob_service_client.get_blob_client(container=container, blob=name)
        blob_client.upload_blob(data, overwrite=True)

def get_experiment_name():
    experiment_env = os.getenv('EXPERIMENT_ENV') or ""
    return str.lower(f"{config['experiment']['name']}{experiment_env}")

def measure(provider, region):
    print(f"measuring: {provider} in {region}")
    env = get_experiment_name()
    id = f"{env}{region}"

    result = None
    if provider in ["azure", "aws", "gcp"]:
        result = subprocess.run(
            [f"/scripts/run_{provider}.sh", id, region], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        raise Exception("Unknown provider!")

    return {'provider': provider, 'region': region, 'result': result}


# Setup logging folder:
Path(log_path).mkdir(parents=True, exist_ok=True)
connect_str = subprocess.check_output(f"az storage account show-connection-string --name {get_experiment_name()}core | jq -r .connectionString", shell=True).decode()
invocations_begin = datetime.now().strftime('%Y%m%dT%H%M%S%f')[:-3]

executor = concurrent.futures.ProcessPoolExecutor(num_launcher)
futs = [executor.submit(measure, pr['provider'], pr['region'])
        for pr in config['experiment-provider-locations']]

fts = concurrent.futures.wait(futs)
# --> timeout, cancel + log that something failed.

invocations_end = datetime.now().strftime('%Y%m%dT%H%M%S%f')[:-3]

json_log = {
    'invocations_begin': invocations_begin,
    'invocations_end': invocations_end,
    'invocations': []
}

for result in fts.done:
    if result.result() != None:
        invocation = {
            'provider': result.result()['provider'],
            'region': result.result()['region'],
            'return_code': result.result()['result'].returncode,
            'stdout': result.result()['result'].stdout.decode('utf-8'),
            'stderr': result.result()['result'].stderr.decode('utf-8')
        }
        json_log['invocations'].append(invocation)

json_file_name = f'{invocations_begin}.json'
with open(os.path.join(log_path, json_file_name), 'w') as outfile:
    json.dump(json_log, outfile, indent=4)
    upload_file(os.path.join(log_path, json_file_name), json_file_name, connect_str, 'runs')
print('invocation finished + logged / uploaded')
