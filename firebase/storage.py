"""
Firebase Storage module for PetTransport app.

This module handles file upload, download and management with Firebase Storage.
"""

import firebase_admin
from firebase_admin import credentials, storage
import os
import json
from datetime import datetime
import google.cloud.storage

# Constants
BUCKET_NAME = "pettransport-b01b8.firebasestorage.app"

# Path to your Firebase service account key file - will be set from environment variable
service_account_key_json = os.getenv("FIREBASE_SERVICE_ACCOUNT", None)
service_account_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "service-account.json"
)

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    # Check for service account file
    if os.path.exists(service_account_path):
        print(f"Initializing Firebase with service account from {service_account_path}")
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred, {"storageBucket": BUCKET_NAME})
    # Try using service account from environment variable
    elif service_account_key_json:
        try:
            service_account_info = json.loads(service_account_key_json)
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred, {"storageBucket": BUCKET_NAME})
            print("Firebase initialized with service account from environment variable")
        except json.JSONDecodeError:
            print(
                "Error: FIREBASE_SERVICE_ACCOUNT environment variable is not valid JSON"
            )
            firebase_admin.initialize_app(options={"storageBucket": BUCKET_NAME})
    else:
        # Initialize without credentials (for local development)
        firebase_admin.initialize_app(options={"storageBucket": BUCKET_NAME})
        print("Firebase initialized without credentials")

# Set up Google Cloud Storage client directly
if os.path.exists(service_account_path):
    # Set environment variable for Google Cloud credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(service_account_path)
    storage_client = google.cloud.storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
else:
    # Fallback to firebase_admin storage
    bucket = storage.bucket()


def upload_file_to_firebase(local_file_path, destination_blob_name=None):
    """
    Uploads a file to Firebase Storage.

    Args:
        local_file_path: Path to the local file to upload
        destination_blob_name: Name to give the file in Firebase Storage
                              If not provided, will use the filename

    Returns:
        Dictionary containing public_url, firebase_path, and blob_name
    """
    if not destination_blob_name:
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = os.path.basename(local_file_path)
        destination_blob_name = f"{timestamp}_{original_filename}"

    blob = bucket.blob(destination_blob_name)

    # Upload the file
    blob.upload_from_filename(local_file_path)

    # Make the blob publicly viewable
    blob.make_public()

    # Return the public URL
    return {
        "public_url": blob.public_url,
        "firebase_path": f"gs://{bucket.name}/{destination_blob_name}",
        "blob_name": destination_blob_name,
    }


def delete_file_from_firebase(blob_name):
    """
    Deletes a file from Firebase Storage.

    Args:
        blob_name: Name of the blob in Firebase Storage

    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        blob = bucket.blob(blob_name)
        blob.delete()
        return True
    except Exception as e:
        print(f"Error deleting file from Firebase: {e}")
        return False


def get_file_url(blob_name):
    """
    Gets the public URL for a file in Firebase Storage.

    Args:
        blob_name: Name of the blob in Firebase Storage

    Returns:
        Public URL of the file
    """
    blob = bucket.blob(blob_name)
    blob.make_public()
    return blob.public_url
