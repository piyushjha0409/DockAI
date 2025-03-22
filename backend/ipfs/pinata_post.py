import requests
import os
from dotenv import load_dotenv

# load enviroment variables

load_dotenv()


def upload_to_pinata(file_path, jwt_token):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "Content-Type": "multipart/form-data",
    }
    with open(file_path, "rb") as file:
        response = requests.post(
            url, files={"file": file}, headers=headers, auth=("Bearer", jwt_token)
        )
        response_data = response.json()
        # return response.json()

        if response.status_code == 202:
            cid = response_data.get("IpfsHash")  # Extract the CID from the response
            return cid

        else:
            print(
                f"Error uplaoding file: {response_data.get('error', 'Unknown error')}"
            )
            return None


# cid = upload_to_pinata(FILE_PATH, PINATA_JWT_TOKEN)
# if cid:
#     print(f"File uploaded with CID: {cid}")


# PINATA_JWT_TOKEN = os.getenv("JWT")

# FILE_PATH = "/test.pdf"

# print(upload_to_pinata(FILE_PATH, PINATA_JWT_TOKEN))
