#!/bin/bash

# This script creates a resource group and the azure container instance
# to run the workload generator (e.g., saaf).
# After deployment the ACI is stopped to reduce cost.

REGION=${3:-"us-east-1"}
ID_CORE=${1}
ID=${2}

# Get Azure Connection String
AZURE_STORAGE_ACCOUNT_KEY=$(az storage account keys list --resource-group $ID_CORE --account-name $ID_CORE | jq .[0].value)
AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string --name $ID_CORE | jq -r .connectionString)


echo $LAMBDA_ARN

# Deploy API Gateway
# Source: https://stackoverflow.com/questions/48740949/lambda-permissions-error-when-setup-using-cloudformation-and-api-gateway-proxy/48752056#48752056
LAMBDA_ARN=$(aws lambda get-function --function-name $ID --region $REGION --query "Configuration.FunctionArn" | jq -r "")
aws cloudformation deploy --template-file cf-templates/apigateway.yml \
                          --region $REGION \
                          --stack-name $ID \
                          --parameter-overrides LambdaArn=$LAMBDA_ARN GeotBenchId=$ID

AWS_REST_API_ID=$(aws cloudformation describe-stack-resources --stack-name $ID --logical-resource-id Api --region $REGION --query "StackResources[0].PhysicalResourceId" | jq -r "")
AWS_API_KEY_ID=$(aws cloudformation describe-stack-resources --stack-name $ID --logical-resource-id ApiKey --region $REGION --query "StackResources[0].PhysicalResourceId" | jq -r "")
AWS_INVOKE_URL="https://${AWS_REST_API_ID}.execute-api.${REGION}.amazonaws.com/prod"
AWS_API_KEY_VALUE=$(aws apigateway get-api-key --api-key $AWS_API_KEY_ID --region $REGION --include-value | jq -r ".value")

echo $AWS_INVOKE_URL

# Deploy Fargate:
aws cloudformation deploy --template-file cf-templates/fargate.yml \
    --stack-name "${ID}-fargate" \
    --region $REGION \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides StorageConnectionString=$AZURE_STORAGE_CONNECTION_STRING GeotBenchId=$ID ApiGatewayEndpoint=$AWS_INVOKE_URL ApiGatewayApiKey=$AWS_API_KEY_VALUE
