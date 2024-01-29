from b2sdk.v2 import InMemoryAccountInfo, B2Api
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve B2 credentials from environment variables
b2_account_id = os.getenv("B2_ACCOUNT_ID")
b2_application_key = os.getenv("B2_APPLICATION_KEY")
b2_bucket_name = os.getenv("B2_BUCKET_NAME")

info = InMemoryAccountInfo()

if __name__ == "__main__":
    b2_api = B2Api(info)
    b2_api.authorize_account("production", b2_account_id, b2_application_key)
    bucket = b2_api.get_bucket_by_name(b2_bucket_name)

    # token = b2_api.get_download_authorization(bucket_name=b2_bucket_name, file_name="test.mp4")
    # print(token)
    token = bucket.get_download_authorization(file_name_prefix="", valid_duration_in_seconds=604800)
    print(token)
