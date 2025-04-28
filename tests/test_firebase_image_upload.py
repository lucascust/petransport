"""Test image uploads to Firebase Storage."""

import os
import datetime
import sys
import tempfile
from PIL import Image

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from new Firebase package structure
from firebase import upload_file_to_firebase


def create_test_image():
    """Create a simple test image"""
    # Create a temporary file
    fd, temp_path = tempfile.mkstemp(suffix=".png")
    os.close(fd)

    # Create a simple colored image
    img = Image.new("RGB", (100, 100), color="red")
    img.save(temp_path)

    return temp_path


def test_image_upload():
    """Test uploading an image to Firebase Storage."""
    print("Starting Firebase Storage image upload test...")

    # Create a test image
    temp_path = create_test_image()
    print(f"Created temporary test image: {temp_path}")

    try:
        # Upload the image to Firebase
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        destination_path = f"test_uploads/test_image_{timestamp}.png"

        print(f"Uploading to Firebase as: {destination_path}")
        result = upload_file_to_firebase(temp_path, destination_path)

        # Display the results
        print("\nUpload successful! Image information:")
        print(f"Public URL: {result['public_url']}")
        print(f"Firebase path: {result['firebase_path']}")
        print(f"Blob name: {result['blob_name']}")

        print("\nTo view your image, open this URL in a browser:")
        print(result["public_url"])

        print("\nTest completed successfully!")
    except Exception as e:
        print(f"\nError during test: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Removed temporary image: {temp_path}")


if __name__ == "__main__":
    test_image_upload()
