import json
import subprocess
import os

config_filename = os.getenv('EXPERIMENT_CONFIG') or ""
if config_filename == "":
    raise Exception('Missing Experiment Config')


config = json.load(open(config_filename))


def get_experiment_name():
    return str.lower(f"{config['experiment']['name']}")


def deploy_saaf_azure(id, region):
    saaf_config = config['saaf-config']
    saaf_config['functionName'] = id
    saaf_config['azureRegion'] = region
    env = get_experiment_name()
    config_name = f"{env}{region}_saaf_config.json"
    with open(config_name, 'w') as outfile:
        json.dump(saaf_config, outfile)
    subprocess.call([f'./SAAF/nodejs_template/deploy/publish.sh',
                    "0", "0", "0", "1", "1024", f"../../../{config_name}"])

def deploy_saaf_aws(id, region):
    saaf_config = config['saaf-config']
    saaf_config['functionName'] = id
    saaf_config['lambdaRegion'] = region
    env = get_experiment_name()
    config_name = f"{env}{region}_saaf_config.json"
    with open(config_name, 'w') as outfile:
        json.dump(saaf_config, outfile)
    subprocess.call([f'./SAAF/nodejs_template/deploy/publish.sh',
                    "1", "0", "0", "0", "1024", f"../../../{config_name}"])

def deploy_saaf_gcp(id, region):
    saaf_config = config['saaf-config']
    saaf_config['functionName'] = id
    saaf_config['googleRegion'] = region
    env = get_experiment_name()
    config_name = f"{env}{region}_saaf_config.json"
    with open(config_name, 'w') as outfile:
        json.dump(saaf_config, outfile)
    subprocess.call([f'./SAAF/nodejs_template/deploy/publish.sh',
                    "0", "1", "0", "0", "1024", f"../../../{config_name}"])

def deploy_azure(id_core, id, region):
    subprocess.call([f'./deploy_azure.sh', id_core, id, region])

def deploy_aws(id_core, id, region):
    subprocess.call([f'./deploy_aws.sh', id_core, id, region])

def deploy_gcp(id_core, id, region):
    subprocess.call([f'./deploy_gcp.sh', id_core, id, region])

def deploy_core(id_core):
    subprocess.call([f'./deploy_core.sh', id_core])

env = get_experiment_name()
id_core = f"{env}core"
deploy_core(id_core) # create resources group and arn for saaf


for pr in config['experiment-provider-locations']:

    provider = pr['provider']
    region = pr['region']

    # shorten id because azure only accepts max 24 chars
    id = f"{env}{region}"[:24]
    
    print(f"deploying {provider} in {region}")

    if provider == "azure": 
        deploy_saaf_azure(id, region)
        deploy_azure(id_core, id, region)

    elif provider == "aws":
        subprocess.call([f'./predeploy_aws.sh', id_core, id, region])

        # TODO: maybe change to boto3
        completed_call = subprocess.check_output(["aws", "iam", "get-role", "--role-name", f"{id}", "--region", f"{region}", "--query", "Role.Arn"])
        arn = json.loads((completed_call.decode('utf8')))

        config['saaf-config']['lambdaRoleARN'] = arn

        deploy_saaf_aws(id, region)
        deploy_aws(id_core, id, region)

    elif  provider == "gcp":
        deploy_saaf_gcp(id, region)
        deploy_gcp(id_core, id, region)

    else:
        print("not implemented")
