# Geot-Faas


This is GEOT-FAAS. An evaluation tooling to observe AWS Lambda, Azure Functions and Google Cloud Functions performance using SAAF.

GEOT-FAAS consists of an evaluation tooling including a central driver (based on an Azure VM), and Container-based workload drivers.

## Deploy a central driver on Azure (you can run the driver also locally):

The `./setup.sh` deploys a VM, and connects to it.
> Clean up via ./setup.sh

```
# install jq
sudo apt-get install jq
# install azure cli
curl -L https://aka.ms/InstallAzureCli | bash

# execute
./setup.sh
```

Clone repo or copy the `docker-compose.yml` to the VM:
```bash
git clone git@github.com:l8518/geot-faas.git
# or
curl https://raw.githubusercontent.com/l8518/geot-faas/main/docker-compose.yml > docker-compose.yml
```

# Setup Evaluation Tooling / Experiment

0. [DEVELOPMENT ONLY] Building Containers
   Copy the `docker-compose.overide.sample.yml` to `docker-compose.override.sample.yml`

   `docker-compose build`

   This will build the docker images for driver and workload generator.

1. Authenticate Central Driver

   The workload driver will deploy resources automatically to the dedicated cloud environments. Thus, you need to authenticate.

   1. Azure: `docker-compose run driver az login` and make sure the right subscription is selected with `az account show` after login.

   2. AWS: `docker-compose run driver aws configure`

       Add `us-east-1` and `json`

   3. GCP: `docker-compose run driver gcloud init`

        Add project id `[select your own]` and change billing under `https://console.cloud.google.com/billing/projects`

        ```bash
        docker-compose run driver gcloud services enable cloudbuild.googleapis.com
        docker-compose run driver gcloud services enable cloudfunctions.googleapis.com
        docker-compose run driver gcloud services enable run.googleapis.com
        docker-compose run driver gcloud services enable artifactregistry.googleapis.com
        ```
2. Configuration:

   You can configure the experiment via docker-compose.override.yml and with a .env file (which is used by docker-compose to see set the environment).

3. Deploy GEOT-FAAS SUT environments `docker-compose run driver python3 deploy_experiment.py`

    > Note: you can control which experiment is being loaded via env var, like: `EXPERIMENT_CONFIG=/scripts/deploy_config_full.json`. Check `docker-compose.yml` to modify across multiple docker-compose invocations.

    > Important: the experiment name needs to be unique. Make sure you mount your own experiment config if you plan to reproduce the results (and not just test).

4. Run Experiment:

   - Via CRON in the background:
     1. make sure you mount an experiment JSON file (see `src/driver/deploy_config_full.json`) for an example.

     2. Adjust the experiment parameters.

     3. Deploy the infrastructure (see above)

     4. Use `docker-compose up -d` 
        > Runs the experiment in the background. To stop use:
        > `docker-compose stop` or `docker-compose down`.

    - Use `docker-compose run sh` and use `run.sh` to take a measurement.

# Analysis Environment

The environment for analysis is based on Jupyter notebooks. You can install the required dependencies via:
```
pip install -r requirements.txt
```

We recommend using a `virtualenv` with `Python 3.7.x`.
Then start the Jupyter environment from the root folder:
```bash
jupyter notebook
# or
python3 -m notebook
```
