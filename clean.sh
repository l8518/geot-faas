#!/bin/bash

read -p "Enter Name Of Experiment: " EXP_NAME

EXP_NAME=${EXP_NAME,,}
REGION="westeurope"
RESOURCE_GROUP="${EXP_NAME}core"
VM_NAME="${EXP_NAME}driver"

az deployment group delete --name AzureDriverDeployment --resource-group $RESOURCE_GROUP
az group delete --name $RESOURCE_GROUP -y

rm ./vmdriver-${EXP_NAME}.key
rm ./vmdriver-${EXP_NAME}.key.pub
