# Geot-Faas

## Setup

1. Build Containers
2. Authenticate Driver

    1. Azure: `docker-compose run driver az login` and make sure the right subscription is selected with `az account show` after login.

    2. AWS: `docker-compose run driver aws configure`

    Add `us-east-1` and `json`

    3. GCP: `docker-compose run driver gcloud init`

    Add project id `[select your own]` and change billing under `https://console.cloud.google.com/billing/projects`

    `docker-compose run driver gcloud services enable cloudbuild.googleapis.com`
    `docker-compose run driver gcloud services enable cloudfunctions.googleapis.com`
    `docker-compose run driver gcloud services enable run.googleapis.com`
    `docker-compose run driver gcloud services enable artifactregistry.googleapis.com`
    

3. Deploy Faas Environment `docker-compose run driver python3 deploy_experiment.py`

## Common Commands

- You can execute all commands from `docker-compose run driver bash` 
   

# Analysis

```
jupyter notebook
or
python3 -m notebook
``` 