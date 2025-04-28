"""Check Firebase configuration details."""

import json
import os
import sys
import os.path
from firebase_admin import credentials, storage, _apps

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_firebase_config():
    """Check Firebase configuration and list available buckets."""
    print("Checking Firebase configuration...")

    # Check service account file
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    service_account_path = os.path.join(root_dir, "service-account.json")

    if os.path.exists(service_account_path):
        print(f"Service account file exists at: {service_account_path}")

        try:
            # Load the service account file
            with open(service_account_path, "r") as f:
                service_account = json.load(f)

            # Print key information (without exposing sensitive data)
            print("\nService Account Info:")
            print(f"Project ID: {service_account.get('project_id', 'Not found')}")
            print(f"Client Email: {service_account.get('client_email', 'Not found')}")

            # Check if there's a private key (without printing it)
            has_private_key = (
                "private_key" in service_account
                and service_account["private_key"].strip()
            )
            if has_private_key:
                print("Has Private Key: Yes")
            else:
                print("Has Private Key: No")

        except json.JSONDecodeError:
            print("ERROR: Service account file is not valid JSON")
        except Exception as e:
            print(f"ERROR reading service account file: {e}")
    else:
        print(f"Service account file not found at: {service_account_path}")

    # Check Firebase initialization
    print("\nFirebase Apps:")
    if not _apps:
        print("No Firebase apps initialized yet")
    else:
        for app_name, app in _apps.items():
            print(f"App name: {app_name}")
            if hasattr(app, "_options") and app._options:
                print(
                    f"Storage bucket: {app._options.get('storageBucket', 'Not configured')}"
                )

    # Get list of available buckets (requires initialized Firebase app)
    try:
        from firebase_admin import initialize_app

        if not _apps:
            # Initialize temporarily if not already initialized
            cred = credentials.Certificate(service_account_path)
            initialize_app(cred)

        # List existing buckets
        client = storage.storage.Client()
        buckets = list(client.list_buckets())

        print("\nAvailable buckets:")
        for bucket in buckets:
            print(f"- {bucket.name}")

        if not buckets:
            print(
                "No buckets found. You may need to create a storage bucket in the Firebase console."
            )

    except Exception as e:
        print(f"\nERROR accessing buckets: {e}")


if __name__ == "__main__":
    check_firebase_config()
