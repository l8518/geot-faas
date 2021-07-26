#!/bin/bash

# This script creates a resource group and the azure container instance
# to run the workload generator (e.g., saaf).
# After deployment the ACI is stopped to reduce cost.

REGION=${3:-"westeurope"}
ID_CORE=${1}
ID=${2}
RESOURCE_GROUP=$ID
IMAGE="ghcr.io/l8518/geot-faas-wrklg:main"
ACI_NAME="workloadgenerator"
AZ_FUNC_NAME=$ID
AZ_FUNC_APP_NAME=$ID
FUNCTION_KEY=$(az functionapp function keys list -n $AZ_FUNC_APP_NAME --function-name $AZ_FUNC_NAME -g $RESOURCE_GROUP | jq -r .default)
FUNCTION_ENDPOINT="https://$AZ_FUNC_APP_NAME.azurewebsites.net/api/$AZ_FUNC_NAME?code=$FUNCTION_KEY"

# Create Resource Group
RG_PROV_STATE=$(az group list --query "[?name=='$RESOURCE_GROUP'] | [0]".properties.provisioningState)

if [ -z "${RG_PROV_STATE}" ]; then
    echo "Resource Group creating"
    az group create --name $RESOURCE_GROUP --location $REGION
else
    echo "Resource Group already exists"
fi

az deployment group create --name ACIDeployment --resource-group $RESOURCE_GROUP \
                           --template-file arm-templates/azure-aci.json \
                           --parameters name=$ACI_NAME \
                                        image=$IMAGE \
                                        logAnalyticsRG=$ID_CORE \
                                        logAnalyticsName="${ID_CORE}-ws" \
                                        location=$REGION \
                                        envSaafEnpoint=$FUNCTION_ENDPOINT \
                                        storageAccountName=$ID_CORE \
                                        storageAccountRG=$ID_CORE
