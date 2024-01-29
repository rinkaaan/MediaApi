from b2sdk.v2 import InMemoryAccountInfo, B2Api
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve B2 credentials from environment variables
b2_account_id = os.getenv("B2_ACCOUNT_ID")
b2_application_key = os.getenv("B2_APPLICATION_KEY")
b2_bucket_name = os.getenv("B2_BUCKET_NAME")
b2_public_bucket_name = os.getenv("B2_PUBLIC_BUCKET_NAME")

info = InMemoryAccountInfo()

def attach_token(url, token):
    return url + "?Authorization=" + token

if __name__ == "__main__":
    b2_api = B2Api(info)
    b2_api.authorize_account("production", b2_account_id, b2_application_key)

    # bucket = b2_api.get_bucket_by_name(b2_bucket_name)
    # url = bucket.get_download_url("thumbnails/Instagram/C0mN_1fP5ql.jpg")
    # token = bucket.get_download_authorization(file_name_prefix="", valid_duration_in_seconds=604800)
    # url = attach_token(url, token)
    # print(url)

    bucket = b2_api.get_bucket_by_name(b2_public_bucket_name)
    url = bucket.get_download_url("test.jpeg")
    print(url)
