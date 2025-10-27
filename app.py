from flask import Flask, request, jsonify, render_template
from azure.storage.blob import BlobServiceClient, ContentSettings
from datetime import datetime
import os
import traceback

AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=casestudy7bnz9cu;AccountKey=+ylYvIc4VZYLaIcf8aLM7n4X1QZCcubKBc7euc1MbINc2jC3oMgPQv6S6dOAFhIMJ+ZfXEzPOeKz+AStNnFNgg==;EndpointSuffix=core.windows.net"
bsc = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
cc  = bsc.get_container_client("lanternfly-images-sf9fbi0j") # Replace with Container name cc.url will get you the url path to the container.  
app = Flask(__name__)
@app.post("/api/v1/upload")
def upload():
    if "file" not in request.files:
        return jsonify(ok=False, error="No file part in the request"), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify(ok=False, error="No file selected"), 400

    filename = f.filename
    try:
        # Upload to Azure Blob Storage
        cc.upload_blob(
            name=filename,
            data=f,
            overwrite=True,
            content_settings=ContentSettings(content_type=f.content_type)
        )

        return jsonify(ok=True, url=f"{cc.url}/{filename}")

    except Exception as e:
        print("Error uploading file:")
        print(traceback.format_exc())  # full traceback in console
        return jsonify(ok=False, error=str(e) or "Unknown error"), 500

@app.get("/api/v1/gallery")
def gallery():
    try:
        blobs = cc.list_blobs()
        image_urls = [f"{cc.url}/{blob.name}" for blob in blobs]

        return jsonify(ok=True, gallery=image_urls)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500
@app.get("/api/v1/health")
def health():
    return jsonify(ok=True, status="healthy")
@app.get("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
  app.run(debug=True)