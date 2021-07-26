#!/bin/bash

EXPERIMENT_NAME="$(date +%Y%m%dT%H%M%SZ)_${WORKLOADGENERATOR_PROVIDER}_${WORKLOADGENERATOR_REGION}"
echo "Running Experiment $EXPERIMENT_NAME"

FUNCTION="../../experiments/basicExperimentFunction.json"
EXPERIMENT="../../experiments/basicExperiment.json"
EXPERIMENT_OUT="../../runs/"

pushd SAAF/test
./faas_runner.py -f $FUNCTION -e $EXPERIMENT -o $EXPERIMENT_OUT
popd
if [ ${WORKLOADGENERATOR_UPLOAD_ARTIFACTS^^} = 'TRUE' ]; then
    mkdir -p upload
    tar -zcvf "upload/$EXPERIMENT_NAME.tar.gz" -C runs .
    python upload.py
fi
