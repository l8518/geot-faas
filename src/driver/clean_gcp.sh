#!/bin/bash

REGION=${3:-"us-east-1"}
ID_CORE=${1}
ID=${2}

# delete aritfacts repro
gcloud artifacts repositories delete $ID_CORE --location=$REGION --async --quiet

# delete cloud run
gcloud run services delete $ID --region=$REGION --quiet

# delete cloud function
gcloud functions delete $ID --region=$REGION --quiet
