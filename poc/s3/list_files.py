import boto3
from b2sdk.v2 import InMemoryAccountInfo, B2Api, FileVersion
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv(dotenv_path="../../api/.env")

# Retrieve B2 credentials from environment variables
aws_access_key_id = os.getenv("B2_ACCOUNT_ID_S3")
aws_secret_access_key = os.getenv("B2_APPLICATION_KEY_S3")
# b2_bucket_name = os.getenv("B2_BUCKET_NAME")
endpoint_url = os.getenv("BACKBLAZE_ENDPOINT")
b2_bucket_name = "nguylinc-photos-test"

s3 = boto3.client(
    "s3",
    endpoint_url=endpoint_url,  # Change this to the appropriate B2 endpoint
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

if __name__ == "__main__":
    # list all files/folders in root of bucket "nguylinc-photos-test", do not list recursively
    response = s3.list_objects_v2(Bucket=b2_bucket_name, Prefix="")
    for file in response["Contents"]:
        print(file["Key"])

    # list buckets
    # response = s3.list_buckets()
    # # print(response)
    # for bucket in response["Buckets"]:
    #     print(bucket["Name"])
