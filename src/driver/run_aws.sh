#!/bin/bash

REGION=${2:-"westeurope"}
ID=${1}

echo $ID
echo $REGION

AWS_VNET_ID=$(aws cloudformation describe-stack-resources --stack-name "${ID}-fargate" --region $REGION --logical-resource-id PublicSubnetOne --query "StackResources[0].PhysicalResourceId" | jq -r "")
nohup aws ecs run-task --cluster "${ID}Cluster" --launch-type FARGATE --task-definition "${ID}TaskDefinition" --region $REGION --network-configuration "awsvpcConfiguration={subnets=[${AWS_VNET_ID}],assignPublicIp=ENABLED}"
