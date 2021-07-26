import os
from azure.storage.blob import BlobServiceClient

print("Upload Artifacts")

log_path = "./upload"

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

def upload_file(fp, name):
    with open(fp, "rb") as data:
        print(f"Uploading {fp} as {name}")
        blob_client = blob_service_client.get_blob_client(container="runs", blob=name)
        blob_client.upload_blob(data, overwrite=True)

# Fetch all files from directory + upload
for path, subdirs, files in os.walk(log_path):
    for name in files:
        fp = os.path.join(path, name)
        upload_file(fp, name)
