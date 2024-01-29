from b2sdk.v2 import InMemoryAccountInfo, B2Api
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve B2 credentials from environment variables
b2_account_id = os.getenv("B2_ACCOUNT_ID")
b2_application_key = os.getenv("B2_APPLICATION_KEY")

info = InMemoryAccountInfo()

if __name__ == "__main__":
    b2_api = B2Api(info)
    b2_api.authorize_account("production", b2_account_id, b2_application_key)
    # b2 rm --versions --recursive <bucket_name>
    # bucket = b2_api.get_bucket_by_name("nguylinc-photos")
    # b2_api.delete_bucket(bucket)
    bucket = b2_api.get_bucket_by_name("nguylinc")
    b2_api.delete_bucket(bucket)
