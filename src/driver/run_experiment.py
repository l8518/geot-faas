import json
from logging import error
import subprocess
import concurrent.futures
import os

num_launcher = 8
config = json.load(open('/scripts/deploy_config.json'))

def get_experiment_name():
    experiment_env = os.getenv('EXPERIMENT_ENV') or ""
    return str.lower(f"{config['experiment']['name']}{experiment_env}")

def measure(provider, region):
    print(f"measuring: {provider} in {region}")
    env = get_experiment_name()
    id = f"{env}{region}" 

    result = None
    if provider in ["azure", "aws", "gcp"]:
       result = subprocess.run([f"/scripts/run_{provider}.sh", id, region], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        raise Exception("Unknown provider!")

    return result


executor = concurrent.futures.ProcessPoolExecutor(num_launcher)
futs = [executor.submit(measure, pr['provider'], pr['region'])
        for pr in config['experiment-provider-locations']]

fts = concurrent.futures.wait(futs)
# --> timeout, cancel + log that something failed.

print("now printing results")

for result in fts.done:
    if result.result() != None:
        print(result.result().returncode)
        print(result.result().stdout.decode('utf-8'))
        print(result.result().stderr.decode('utf-8'))
