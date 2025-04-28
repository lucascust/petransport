"""A simple Flask app to test Firebase Storage uploads."""

import os
import sys
import tempfile
import datetime
from flask import Flask, request, redirect, flash
from werkzeug.utils import secure_filename

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from new Firebase package structure
from firebase import upload_file_to_firebase

# Create a simple Flask app
app = Flask(__name__)
app.secret_key = "test_secret_key"
app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static/uploads"
)

# Ensure the upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def index():
    """Render the home page with file upload form."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Firebase Storage Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; margin: 0 auto; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; }
            .btn { padding: 10px 15px; background-color: #4285f4; color: white; border: none; cursor: pointer; }
            .result { margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 4px; }
            img { max-width: 100%; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Firebase Storage Upload Test</h1>
            
            <form action="/upload" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="file">Select file to upload:</label>
                    <input type="file" name="file" id="file" required>
                </div>
                <button type="submit" class="btn">Upload to Firebase</button>
            </form>
        </div>
    </body>
    </html>
    """


@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload to Firebase Storage."""
    # Check if a file was uploaded
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file")
        return redirect(request.url)

    # Process the file
    if file:
        # Save the file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{timestamp}_{filename}"
        temp_path = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)

        try:
            # Save locally first
            file.save(temp_path)

            # Upload to Firebase
            destination_blob_name = f"flask_test/{temp_filename}"
            result = upload_file_to_firebase(temp_path, destination_blob_name)

            # Remove the temporary file
            os.remove(temp_path)

            # Create the result page
            is_image = filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Upload Success</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    .result {{ margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 4px; }}
                    img {{ max-width: 100%; margin-top: 10px; }}
                    pre {{ background-color: #eee; padding: 10px; overflow-x: auto; }}
                    .success {{ color: green; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Upload Successful!</h1>
                    
                    <div class="result">
                        <h2>File Information:</h2>
                        <p><strong>Original filename:</strong> {filename}</p>
                        <p><strong>Firebase path:</strong> {result['firebase_path']}</p>
                        <p><strong>Public URL:</strong> <a href="{result['public_url']}" target="_blank">{result['public_url']}</a></p>
                        
                        {'<h3>Preview:</h3>' if is_image else ''}
                        {'<img src="' + result['public_url'] + '" alt="Uploaded image">' if is_image else ''}
                    </div>
                    
                    <div class="result">
                        <h2>Raw Response:</h2>
                        <pre>{str(result)}</pre>
                    </div>
                    
                    <p><a href="/">Upload another file</a></p>
                </div>
            </body>
            </html>
            """

            return html

        except Exception as e:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Upload Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .error {{ color: red; background-color: #ffeeee; padding: 10px; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Upload Error</h1>
                    <div class="error">
                        <p>An error occurred during file upload:</p>
                        <p>{str(e)}</p>
                    </div>
                    <p><a href="/">Try again</a></p>
                </div>
            </body>
            </html>
            """


if __name__ == "__main__":
    app.run(debug=True, port=5001)
