#!/bin/bash

REGION=${2:-"westeurope"}
ID=${1}
RESOURCE_GROUP=$ID
ACI_NAME="workloadgenerator"

ACI_PROV_STATUS=$(az container list --query "[?resourceGroup=='$RESOURCE_GROUP' && name=='$ACI_NAME'] | [0]" | jq ".provisioningState")
echo $ACI_PROV_STATUS
if [ $ACI_PROV_STATUS = '"Succeeded"' ]; then
    echo "ACI Run Workload"
    az container start -g $RESOURCE_GROUP -n $ACI_NAME
else
    echo "Something went wrong here"
fi
