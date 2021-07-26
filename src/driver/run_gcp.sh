#!/bin/bash

REGION=${2:-"westeurope"}
ID=${1}

echo $ID
echo $REGION

ENDPOINT=$(gcloud run services describe $ID --region=$REGION --format=json | jq -r ".status.url")

curl --header "Content-Type: application/json" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  --request POST \
  --data "{\"token-key\":\"Authorization\",\"token-value\":\"Bearer $(gcloud auth print-identity-token)\"}" \
   $ENDPOINT
