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
    bucket = b2_api.get_bucket_by_name("nguylinc")
    # bucket.upload_local_file(
    #     local_file="./test.mp4",
    #     file_name="hello/world/test.mp4",
    # )
    file = bucket.get_file_info_by_name("hello/world/test.mp4")
    file.delete()
