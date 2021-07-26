#!/bin/bash

# This script creates a resource group and the azure container instance
# to run the workload generator (e.g., saaf).
# After deployment the ACI is stopped to reduce cost.

REGION=${3:-"us-east-1"}
ID_CORE=${1}
ID=${2}

# delete other stuff
aws cloudformation delete-stack --stack-name $ID --region $REGION
aws cloudformation delete-stack --stack-name "${ID}-fargate" --region $REGION

# delete saaf stuf:
aws lambda delete-function --function-name $ID --region $REGION
aws iam detach-role-policy --role-name $ID --region $REGION --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name $ID --region $REGION