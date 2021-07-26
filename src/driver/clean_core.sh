#!/bin/bash

# This script creates a resource group and the azure container instance
# to run the workload generator (e.g., saaf).
# After deployment the ACI is stopped to reduce cost.

REGION="westeurope"
ID_CORE=${1}
RESOURCE_GROUP=$ID_CORE

echo "cleaning core"

az deployment group delete --name AzureCoreDeployment --resource-group $RESOURCE_GROUP --no-wait
