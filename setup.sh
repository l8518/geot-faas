#!/bin/bash

read -p "Enter Name Of Experiment: " EXP_NAME

EXP_NAME=${EXP_NAME,,}
REGION="westeurope"
RESOURCE_GROUP="${EXP_NAME}core"
VM_NAME="${EXP_NAME}driver"

RG_PROV_STATE=$(az group list --query "[?name=='$RESOURCE_GROUP'] | [0]".properties.provisioningState)

if [ -z "${RG_PROV_STATE}" ]; then
    echo "Resource Group creating"
    az group create --name $RESOURCE_GROUP --location $REGION
else
    echo "Resource Group already exists"
fi

ssh-keygen -m PEM -t rsa -b 4096 -P "" -f "./vmdriver-${EXP_NAME}.key"
PK=$(cat "./vmdriver-${EXP_NAME}.key.pub")
USERNAME=$EXP_NAME

az deployment group create --name AzureDriverDeployment \
    --resource-group $RESOURCE_GROUP \
    --template-file azure-driver.json \
    --parameters vmname=$VM_NAME adminUsername=$EXP_NAME adminPublicKey="$PK"

VM_IP=$(az vm list-ip-addresses -n "$VM_NAME-vm" -g $RESOURCE_GROUP --query [0].virtualMachine.network.publicIpAddresses[0].ipAddress -o tsv)

echo "ssh $EXP_NAME@$VM_IP -i \"vmdriver-${EXP_NAME}.key\""
echo "keep this command in mind to login again (note: vm keeps running on Azure)"
