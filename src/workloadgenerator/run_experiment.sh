#!/bin/bash
WORKLOAD_GENERATOR_TIME_START=$(date +%Y%m%dT%H%M%SZ)
EXPERIMENT_NAME="${WORKLOAD_GENERATOR_TIME_START}_${WORKLOADGENERATOR_PROVIDER}_${WORKLOADGENERATOR_REGION}"
FUNCTION="../../experiments/basicExperimentFunction.json"
EXPERIMENT="../../experiments/basicExperiment.json"
EXPERIMENT_OUT="../../runs/"

echo "Running Experiment $EXPERIMENT_NAME"

# Run Faas Runner
pushd SAAF/test > /dev/null
mkdir -p "$EXPERIMENT_OUT"
WORKLOAD_GENERATOR_TIME_FAAS_RUNNER_START=$(date +%Y%m%dT%H%M%SZ)
./faas_runner.py -f $FUNCTION -e $EXPERIMENT -o $EXPERIMENT_OUT &> "${EXPERIMENT_OUT}${EXPERIMENT_NAME}.out"
WORKLOAD_GENERATOR_TIME_FAAS_RUNNER_END=$(date +%Y%m%dT%H%M%SZ)
popd > /dev/null

if [ ${WORKLOADGENERATOR_UPLOAD_ARTIFACTS^^} = 'TRUE' ]; then
    mkdir -p upload

    # Tar Faas Runner Results
    WORKLOAD_GENERATOR_TIME_TAR_START=$(date +%Y%m%dT%H%M%SZ)
    tar -zcf "upload/$EXPERIMENT_NAME.tar.gz" -C runs .
    WORKLOAD_GENERATOR_TIME_TAR_END=$(date +%Y%m%dT%H%M%SZ)

    # Upload Faas Runner Results
    WORKLOAD_GENERATOR_TIME_UPLOAD_START=$(date +%Y%m%dT%H%M%SZ)
    ./upload.sh "upload/$EXPERIMENT_NAME.tar.gz" "$EXPERIMENT_NAME.tar.gz"
    if [ $? -eq 0 ]; then
        echo "OK: TAR UPLOADED"
    else
        echo "ERROR: TAR FAILED TO UPLOAD!"
    fi
    WORKLOAD_GENERATOR_TIME_UPLOAD_END=$(date +%Y%m%dT%H%M%SZ)

fi

echo "WORKLOAD_GENERATOR_TIME_START             $WORKLOAD_GENERATOR_TIME_START"
echo "WORKLOAD_GENERATOR_TIME_FAAS_RUNNER_START $WORKLOAD_GENERATOR_TIME_FAAS_RUNNER_START"
echo "WORKLOAD_GENERATOR_TIME_FAAS_RUNNER_END   $WORKLOAD_GENERATOR_TIME_FAAS_RUNNER_END"
echo "WORKLOAD_GENERATOR_TIME_TAR_START         $WORKLOAD_GENERATOR_TIME_TAR_START"
echo "WORKLOAD_GENERATOR_TIME_TAR_END           $WORKLOAD_GENERATOR_TIME_TAR_END"
echo "WORKLOAD_GENERATOR_TIME_UPLOAD_START      $WORKLOAD_GENERATOR_TIME_UPLOAD_START"
echo "WORKLOAD_GENERATOR_TIME_UPLOAD_END        $WORKLOAD_GENERATOR_TIME_UPLOAD_END"
