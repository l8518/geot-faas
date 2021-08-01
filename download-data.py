import os
import subprocess
from pathlib import Path

from azure.storage.blob import BlobServiceClient

experimentname = input("Enter experiment name:")

connect_str = subprocess.check_output(
    f"az storage account show-connection-string --name {experimentname}core | jq -r .connectionString", shell=True).decode()
download_path = f"./data/downloaded/{experimentname}"
Path(download_path).mkdir(parents=True, exist_ok=True)

blob_service = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service.get_container_client("runs")
# List the blobs in the container:
blob_list = container_client.list_blobs()

# List the already downloaded elements:
downloaded_tars = os.listdir(download_path)

print(downloaded_tars)
for blob in blob_list:
    if blob.name in downloaded_tars:
        print(f"{blob.name} already downloaded, skipping")
        continue

    blob_client = blob_service.get_blob_client(container="runs", blob=blob)
    download_file_path = os.path.join(download_path, blob.name)
    print("\nDownloading blob to \n\t" + download_file_path)

    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

print("downloaded")
