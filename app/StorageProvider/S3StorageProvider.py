from app.StorageProvider.BaseStorageProvider import BaseStorageProvider
from app.internal.config import TSDATA, S3_URL, S3_MODEL_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_KEY
import boto3
import numpy as np
from io import BytesIO

class S3StorageProvider(BaseStorageProvider):


    def __init__(self):
        self.s3 = boto3.client(service_name='s3', endpoint_url=S3_URL, aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_KEY)
        
        if not self.s3.head_bucket(Bucket=S3_MODEL_BUCKET_NAME):
            self.s3.create_bucket(Bucket=S3_MODEL_BUCKET_NAME)

    def save(self, id, data):
        id = str(id)
        self.s3.put_object(Bucket=S3_MODEL_BUCKET_NAME, Key=id, Body=data)
        print("Series saved to S3 successfully.")
    
    def load(cls, id):
        id = str(id)
        response = cls.s3.get_object(Bucket=S3_MODEL_BUCKET_NAME, Key=id)
        return response['Body'].read()

    def delete(cls, id):
        id = str(id)
        cls.s3.delete_object(Bucket=S3_MODEL_BUCKET_NAME, Key=id)
        print(f"Series with id {id} deleted from S3.")