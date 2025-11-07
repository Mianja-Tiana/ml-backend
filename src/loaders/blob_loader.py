from azure.storage.blob import BlobServiceClient
from pathlib import Path
import os

class BlobLoader:
    def __init__(self):
        self.conn_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        self.container_name = os.environ["AZURE_STORAGE_CONTAINER_NAME"]

        self.client = BlobServiceClient.from_connection_string(self.conn_str)

    def download(self, blob_path: str, local_path: str):
        container = self.client.get_container_client(self.container_name)
        blob = container.get_blob_client(blob_path)
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            data = blob.download_blob().readall()
            f.write(data)
        return local_path
