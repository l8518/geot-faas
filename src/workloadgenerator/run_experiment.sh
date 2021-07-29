#!/bin/bash

EXPERIMENT_NAME="$(date +%Y%m%dT%H%M%SZ)_${WORKLOADGENERATOR_PROVIDER}_${WORKLOADGENERATOR_REGION}"
echo "Running Experiment $EXPERIMENT_NAME"

FUNCTION="../../experiments/basicExperimentFunction.json"
EXPERIMENT="../../experiments/basicExperiment.json"
EXPERIMENT_OUT="../../runs/"

pushd SAAF/test
mkdir -p "$EXPERIMENT_OUT"
./faas_runner.py -f $FUNCTION -e $EXPERIMENT -o $EXPERIMENT_OUT &> "${EXPERIMENT_OUT}${EXPERIMENT_NAME}.out"
popd
if [ ${WORKLOADGENERATOR_UPLOAD_ARTIFACTS^^} = 'TRUE' ]; then
    mkdir -p upload
    tar -zcf "upload/$EXPERIMENT_NAME.tar.gz" -C runs .
    ./upload.sh "upload/$EXPERIMENT_NAME.tar.gz" "$EXPERIMENT_NAME.tar.gz"
    UPLOAD_SUCCESS=$?
    echo $UPLOAD_SUCCESS
    if [ $UPLOAD_SUCCESS -eq 0 ]; then
        echo "OK: TAR UPLOADED"
    else
        echo "ERROR: TAR FAILED TO UPLOAD!"
    fi
fi
