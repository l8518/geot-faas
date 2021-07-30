#!/bin/bash

INVOCATION_START=$(date +%Y%m%dT%H%M%S%3N)
REGION=${2:-"europe-west1"}
ID=${1}

echo "====================" 
echo "Invoking Workloadgenerator"
echo "Provider:                    GCP"
echo "Region:                      $REGION"
echo "ID:                          $ID"

echo "====Gcp Stats====" 
echo "====================" 

INVOCATION_ENDPOINT_START=$(date +%Y%m%dT%H%M%S%3N)
ENDPOINT=$(gcloud run services describe $ID --region=$REGION --format=json | jq -r ".status.url")
INVOCATION_ENDPOINT_END=$(date +%Y%m%dT%H%M%S%3N)

INVOCATION_BEARER_START=$(date +%Y%m%dT%H%M%S%3N)
BEARER_TOKEN=$(gcloud auth print-identity-token)
INVOCATION_BEARER_END=$(date +%Y%m%dT%H%M%S%3N)

INVOCATION_CURL_START=$(date +%Y%m%dT%H%M%S%3N)
CURL_HTTP_CODE=$(curl \
    --write-out "%{http_code}\n" --silent \
    --output upload.log \
    -s  \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $BEARER_TOKEN" \
    --request POST \
    --data "{\"token-key\":\"Authorization\",\"token-value\":\"Bearer $BEARER_TOKEN\"}" \
    $ENDPOINT
   )

INVOCATION_CURL_END=$(date +%Y%m%dT%H%M%S%3N)

echo "====================" 
echo "Finished Workloadgenerator "
echo "CURL_HTTP_CODE               $CURL_HTTP_CODE"
echo "INVOCATION_START             $INVOCATION_START"
echo "INVOCATION_ENDPOINT_START    $INVOCATION_ENDPOINT_START"
echo "INVOCATION_ENDPOINT_END      $INVOCATION_ENDPOINT_END"
echo "INVOCATION_BEARER_START      $INVOCATION_BEARER_START"
echo "INVOCATION_BEARER_END        $INVOCATION_BEARER_END"
echo "INVOCATION_CURL_START        $INVOCATION_CURL_START"
echo "INVOCATION_CURL_END          $INVOCATION_CURL_END"
echo "===================="
