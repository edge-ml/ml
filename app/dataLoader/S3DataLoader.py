from app.dataLoader.BaseDataLoader import BaseDataLoader
from app.internal.config import S3_URL, S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_KEY
import boto3
import h5py
import numpy as np
from io import BytesIO

class S3DataLoader(BaseDataLoader):
    def __init__(self):
        self.s3 = boto3.client(service_name='s3', endpoint_url=S3_URL, aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_KEY)
        self.s3.create_bucket(Bucket=S3_BUCKET_NAME)

    def load_series(self, id):
        obj = self.s3.get_object(Bucket=S3_BUCKET_NAME, Key=id)
        print(obj)
        buffer = BytesIO(obj['Body'].read())
        with h5py.File(buffer, 'r') as f:
            time_arr = np.array(f['time'])
            data_arr = np.array(f['data'])
            return time_arr, data_arr

    def save_series(self, id, time_arr, data_arr):
        buffer = BytesIO()
        with h5py.File(buffer, 'w') as f:
            f.create_dataset('time', data=time_arr)
            f.create_dataset('data', data=data_arr)
        buffer.seek(0)
        self.s3.put_object(Bucket=S3_BUCKET_NAME, Key=id, Body=buffer.getvalue())
        print("Series saved to S3 successfully.")


    def delete(self, id):
        self.s3.delete_object(Bucket=S3_BUCKET_NAME, Key=id)
        print(f"Object with id {id} deleted successfully.")