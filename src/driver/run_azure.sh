#!/bin/bash

INVOCATION_START=$(date +%Y%m%dT%H%M%S%3N)

REGION=${2:-"westeurope"}
ID=${1}
RESOURCE_GROUP=$ID
ACI_NAME="workloadgenerator"

echo "====================" 
echo "Invoking Workloadgenerator"
echo "Provider:                    AZURE"
echo "Region:                      $REGION"
echo "ID:                          $ID"

echo "====Azure Stats====" 
echo "ACI_NAME:                    $ACI_NAME"
echo "RESOURCE_GROUP:              $RESOURCE_GROUP"
echo "====================" 

INVOCATION_ACI_START=$(date +%Y%m%dT%H%M%S%3N)
az container start -g $RESOURCE_GROUP -n $ACI_NAME
ACI_RET=$?
INVOCATION_ACI_END=$(date +%Y%m%dT%H%M%S%3N)

echo "====================" 
echo "Finished Workloadgenerator "
echo "ACI RETURN CODE              $ACI_RET"
echo "INVOCATION_START             $INVOCATION_START"
echo "INVOCATION_ACI_START         $INVOCATION_ACI_START"
echo "INVOCATION_ACI_END           $INVOCATION_ACI_END"
echo "====================" 
