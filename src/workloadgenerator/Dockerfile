FROM python:3.6

# AWS, AZURE or GCP
ENV WORKLOADGENERATOR_PROVIDER=UNKNOW
ENV WORKLOADGENERATOR_REGION=UNKNOW
ENV WORKLOADGENERATOR_UPLOAD_ARTIFACTS=FALSE
ENV AZURE_STORAGE_CONNECTION_STRING=UNDEFINED
ENV SAAF_ENDPOINT=
ENV SAAF_ENDPOINT_HEADERS="{}"
ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app
# Install Python Dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install SAAF
RUN git clone https://github.com/l8518/SAAF.git --depth 1

# Add remaning sources
COPY . .

# ENTRYPOINT /app/entrypoint.sh
CMD /app/run.sh
