#!/bin/bash

REGION=${3:-"westeurope"}
ID_CORE=${1}
ID=${2}
RESOURCE_GROUP=$ID

az group delete --name $RESOURCE_GROUP -y --no-wait
