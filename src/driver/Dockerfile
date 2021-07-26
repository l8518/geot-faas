FROM ubuntu:18.04

ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
ENV EXPERIMENT_ENV=

# Add Docker CLI
RUN apt-get update && apt-get install  -y apt-transport-https ca-certificates curl gnupg lsb-release && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
  
# Add base dependencies
RUN apt update && apt -y install cron jq git unzip zip docker-ce-cli

# Install Azure Dependencies
RUN apt-get update && \
    apt-get install -y ca-certificates curl apt-transport-https lsb-release gnupg && \
    curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/azure-cli.list && \
    sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list' && \
    apt-get update && apt-get install -y azure-cli=2.25.0-1~bionic azure-functions-core-tools-3=3.0.3568-1

# Install Instal AWS Dependencies
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.2.15.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

# Install GCP Dependencies
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get install apt-transport-https ca-certificates gnupg && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-sdk=347.0.0-0 

WORKDIR /scripts

# Install SAAF
RUN git clone https://github.com/l8518/SAAF.git --depth 1

# Setup Cron To Execute the run.sh
COPY cron /etc/cron.d/cron
RUN crontab /etc/cron.d/cron && touch /var/log/cron.log

# COPY scripts
COPY . .

# Run the command on container startup
CMD export > /.env && cron && tail -f /var/log/cron.log
