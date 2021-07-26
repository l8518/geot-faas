#!/bin/bash

# This script creates a resource group and the azure container instance
# to run the workload generator (e.g., saaf).
# After deployment the ACI is stopped to reduce cost.

REGION=${3:-"us-east-1"}
ID_CORE=${1}
ID=${2}

# -------------------------------- AWS
echo "AWS Configuration"
aws iam get-role --role-name $ID
if [ "$?" != 0 ]; then
    aws iam create-role --role-name $ID --region $REGION --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
    aws iam attach-role-policy --role-name $ID --region $REGION --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    sleep 30 # otherwise lambda creation fails
fi
