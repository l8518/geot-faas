#!/bin/bash

# This script creates a resource group and the azure container instance
# to run the workload generator (e.g., saaf).
# After deployment the ACI is stopped to reduce cost.

REGION="westeurope"
ID_CORE=${1}
RESOURCE_GROUP=$ID_CORE

# ------------------------------- AZURE
# Create Resource Group
RG_PROV_STATE=$(az group list --query "[?name=='$RESOURCE_GROUP'] | [0]".properties.provisioningState)

if [ -z "${RG_PROV_STATE}" ]; then
    echo "Resource Group creating"
    az group create --name $RESOURCE_GROUP --location $REGION
else
    echo "Resource Group already exists"
fi


az deployment group create --name AzureCoreDeployment --resource-group $RESOURCE_GROUP --template-file arm-templates/azure-core.json --parameters storageAccounts_name=$ID_CORE workspaces_name="$ID_CORE-ws" region=$REGION
