#!/bin/bash

INVOCATION_START=$(date +%Y%m%dT%H%M%S%3N)
REGION=${2:-"westeurope"}
ID=${1}


echo "====================" 
echo "Invoking Workloadgenerator"
echo "Provider:                    AWS"
echo "Region:                      $REGION"
echo "ID:                          $ID"

echo "====Aws Stats====" 
echo "====================" 

INVOCATION_VNET_START=$(date +%Y%m%dT%H%M%S%3N)
AWS_VNET_ID=$(aws cloudformation describe-stack-resources --stack-name "${ID}-fargate" --region $REGION --logical-resource-id PublicSubnetOne --query "StackResources[0].PhysicalResourceId" | jq -r "")
INVOCATION_VNET_END=$(date +%Y%m%dT%H%M%S%3N)

INVOCATION_FARGATE_START=$(date +%Y%m%dT%H%M%S%3N)
aws ecs run-task --cluster "${ID}Cluster" --launch-type FARGATE --task-definition "${ID}TaskDefinition" --region $REGION --network-configuration "awsvpcConfiguration={subnets=[${AWS_VNET_ID}],assignPublicIp=ENABLED}"
RUN_TASK_RET=$?
INVOCATION_FARGATE_END=$(date +%Y%m%dT%H%M%S%3N)

echo "====================" 
echo "Finished Workloadgenerator "
echo "RUN_TASK_RET RETURN CODE     $RUN_TASK_RET"
echo "INVOCATION_START             $INVOCATION_START"
echo "INVOCATION_VNET_START        $INVOCATION_VNET_START"
echo "INVOCATION_VNET_END          $INVOCATION_VNET_END"
echo "INVOCATION_FARGATE_START     $INVOCATION_FARGATE_START"
echo "INVOCATION_FARGATE_END       $INVOCATION_FARGATE_END"
echo "===================="
