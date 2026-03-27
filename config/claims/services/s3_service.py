import boto3
import os
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="ap-south-1"
)

def upload_to_s3(file, file_name):
    try:
        s3.upload_fileobj(file, "claimguard", file_name)
        return f"https://claimguard.s3.amazonaws.com/{file_name}"
    except Exception as e:
        print("ERROR:", str(e))
        raise e