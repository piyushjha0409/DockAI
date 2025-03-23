import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def upload_to_pinata(file_path, jwt_token):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    if not jwt_token:
        print("Error: Missing JWT token")
        return None

    headers = {
        "Authorization": f"Bearer {jwt_token}"
        # Do NOT set "Content-Type" manually for multipart file uploads
    }

    try:
        with open(file_path, "rb") as file:
            response = requests.post(
                url, files={"file": file}, headers=headers
            )
            response_data = response.json()

            if response.status_code == 200:  # Pinata returns 200 on success
                cid = response_data.get("IpfsHash")  # Extract the CID from the response
                print(f"File uploaded successfully with CID: {cid}")
                return cid
            else:
                print(
                    f"Error uploading file: {response_data.get('error', 'Unknown error')}"
                )
                return None
    except Exception as e:
        print(f"HTTP Exception: Failed to upload PDF to Pinata. Error: {e}")
        return None


# Example usage
PINATA_JWT_TOKEN = os.getenv("JWT")  # Ensure this is set in your .env file
FILE_PATH = "/test.pdf"  # Replace with the path to your file

if PINATA_JWT_TOKEN and os.path.exists(FILE_PATH):
    cid = upload_to_pinata(FILE_PATH, PINATA_JWT_TOKEN)
    if cid:
        print(f"File uploaded with CID: {cid}")
else:
    print("Error: JWT token or file path is missing or invalid.")