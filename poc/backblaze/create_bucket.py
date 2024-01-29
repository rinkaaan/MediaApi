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

life_cycle_rules = [{
    "daysFromHidingToDeleting": 1,
    "daysFromUploadingToHiding": None,
    "fileNamePrefix": ""
}]

if __name__ == "__main__":
    b2_api = B2Api(info)
    b2_api.authorize_account("production", b2_account_id, b2_application_key)
    # b2_api.create_bucket(b2_bucket_name, "allPrivate", lifecycle_rules=life_cycle_rules)
    # b2_api.create_bucket(b2_public_bucket_name, "allPublic", lifecycle_rules=life_cycle_rules)
    b2_api.create_bucket(b2_bucket_name, "allPublic", lifecycle_rules=life_cycle_rules)
