"""List available Firebase Storage buckets."""

import os
import sys
from google.cloud import storage

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def list_available_buckets():
    """Lists all available buckets in the GCP project."""

    # Set up the credentials explicitly
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    service_account_path = os.path.join(root_dir, "service-account.json")

    if os.path.exists(service_account_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(
            service_account_path
        )

    # Create storage client
    try:
        storage_client = storage.Client()

        print("Listing available buckets:")
        buckets = list(storage_client.list_buckets())

        if not buckets:
            print("No buckets found in your GCP project.")
            print("You need to create a storage bucket first.")
            print("Visit: https://console.cloud.google.com/storage/browser")
            return

        print(f"Found {len(buckets)} bucket(s):")
        for bucket in buckets:
            print(f"- {bucket.name}")

    except Exception as e:
        print(f"Error listing buckets: {e}")


if __name__ == "__main__":
    list_available_buckets()
