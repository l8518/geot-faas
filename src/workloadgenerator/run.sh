#!/bin/bash

if [ ${WORKLOADGENERATOR_PROVIDER^^} = 'GCP' ]; then
    PORT=80
    exec gunicorn --bind :$PORT --workers 1 --threads 1 --timeout 0 --log-level debug gcpcloudrun:app
else
    source /app/run_experiment.sh
fi
