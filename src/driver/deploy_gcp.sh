#!/bin/bash

# This script creates a resource group and the azure container instance
# to run the workload generator (e.g., saaf).
# After deployment the ACI is stopped to reduce cost.

REGION=${3:-"us-east-1"}
ID_CORE=${1}
ID=${2}
IMAGE="ghcr.io/l8518/geot-faas-wrklg:main"
PORT=80

# Get Azure Connection String
AZURE_STORAGE_ACCOUNT_KEY=$(az storage account keys list --resource-group $ID_CORE --account-name $ID_CORE | jq .[0].value)
AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string --name $ID_CORE | jq -r .connectionString)


GCP_ENDPOINT=$(gcloud functions describe $ID --region $REGION --format=json | jq -r ".httpsTrigger.url")
GCP_PROJECT_ID=$(gcloud config list --format 'value(core.project)')


gcloud auth configure-docker $REGION-docker.pkg.dev --quiet
gcloud artifacts repositories create $ID_CORE --repository-format=docker --location=$REGION

docker pull $IMAGE
docker tag $IMAGE $REGION-docker.pkg.dev/$GCP_PROJECT_ID/$ID_CORE/workloadgenerator:LATEST
docker push $REGION-docker.pkg.dev/$GCP_PROJECT_ID/$ID_CORE/workloadgenerator:LATEST

echo $GCP_ENDPOINT
gcloud run deploy $ID --image $REGION-docker.pkg.dev/$GCP_PROJECT_ID/$ID_CORE/workloadgenerator:LATEST \
                      --timeout=3600 \
                      --memory=2Gi \
                      --cpu=2 \
                      --port=$PORT --region=$REGION --quiet \
                      --set-env-vars=WORKLOADGENERATOR_PROVIDER=GCP,WORKLOADGENERATOR_REGION=$REGION,SAAF_ENDPOINT=$GCP_ENDPOINT,AZURE_STORAGE_CONNECTION_STRING=$AZURE_STORAGE_CONNECTION_STRING,WORKLOADGENERATOR_UPLOAD_ARTIFACTS=TRUE
