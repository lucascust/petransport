"""Test file uploads to Firebase Storage."""

import os
import tempfile
import datetime
import sys
import os.path

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from new Firebase package structure
from firebase import upload_file_to_firebase, get_file_url


def test_firebase_upload():
    """Test uploading a text file to Firebase Storage."""
    print("Starting Firebase Storage upload test...")

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
        temp_path = temp.name
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"This is a test file created at {current_time}\n"
        temp.write(content.encode("utf-8"))

    print(f"Created temporary test file: {temp_path}")

    try:
        # Upload the file to Firebase
        destination_path = f"test_uploads/test_file_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        print(f"Uploading to Firebase as: {destination_path}")
        result = upload_file_to_firebase(temp_path, destination_path)

        # Display the results
        print("\nUpload successful! File information:")
        print(f"Public URL: {result['public_url']}")
        print(f"Firebase path: {result['firebase_path']}")
        print(f"Blob name: {result['blob_name']}")

        # Verify we can get the URL again
        url = get_file_url(result["blob_name"])
        print(f"\nVerified public URL: {url}")

        print("\nTest completed successfully!")
    except Exception as e:
        print(f"\nError during test: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Removed temporary file: {temp_path}")


if __name__ == "__main__":
    test_firebase_upload()
