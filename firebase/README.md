# Firebase Storage Integration for PetTransport

This module provides Firebase Storage functionality for the PetTransport application.

## Features

- Upload files to Firebase Storage with automatic public URL generation
- Download files from Firebase Storage
- Delete files from Firebase Storage
- Automatic handling of authentication and permissions

## Usage

```python
from firebase import upload_file_to_firebase, delete_file_from_firebase, get_file_url

# Upload a file to Firebase Storage
result = upload_file_to_firebase('/path/to/local/file.pdf', 'destination/filename.pdf')
print(f"File uploaded to: {result['public_url']}")

# Get the public URL for a file
url = get_file_url('destination/filename.pdf')

# Delete a file
success = delete_file_from_firebase('destination/filename.pdf')
```

## Configuration

The module automatically loads Firebase configuration from:

1. A service account key file (`service-account.json`) in the project root
2. The `FIREBASE_SERVICE_ACCOUNT` environment variable

See the detailed setup guide in `/docs/FIREBASE_SETUP.md`. 