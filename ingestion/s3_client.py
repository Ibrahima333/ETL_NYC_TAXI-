import os
import boto3
from dotenv import load_dotenv
from botocore.config import Config



BUCKET_NAME = "nyc-taxi-bronze"

#chargement des variables d'environement
load_dotenv()

# Créer le client S3
s3_client = boto3.client(
    "s3",

    endpoint_url="http://localhost:9000",

    aws_access_key_id=os.getenv("RUSTFS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("RUSTFS_SECRET_KEY"),

    region_name="us-east-1",

    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"}
    )
)



def upload_file_to_s3(file_path, bucket_name, object_name):
    s3_client.upload_file(
        str(file_path),
        bucket_name,
        object_name
    )

    print(f"Fichier envoyé : {object_name}")


