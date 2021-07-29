FROM alpine/git as build

WORKDIR /app
RUN git clone https://github.com/l8518/SAAF.git --depth 1

FROM python:3.6-slim

# AWS, AZURE or GCP
ENV WORKLOADGENERATOR_PROVIDER=UNKNOW
ENV WORKLOADGENERATOR_REGION=UNKNOW
ENV WORKLOADGENERATOR_UPLOAD_ARTIFACTS=FALSE
ENV AZURE_STORAGE_CONNECTION_STRING=UNDEFINED
ENV AZURE_CONTAINER_NAME=runs
ENV SAAF_ENDPOINT=
ENV SAAF_ENDPOINT_HEADERS="{}"
ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app

RUN apt update && apt install -y file curl xxd

# Install Python Dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install SAAF
COPY --from=build /app/SAAF ./SAAF

# Add remaning sources
COPY . .

# ENTRYPOINT /app/entrypoint.sh
CMD /app/run.sh
