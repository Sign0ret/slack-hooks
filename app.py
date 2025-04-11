from fastapi import FastAPI, Request, UploadFile, File
import requests
from dotenv import load_dotenv
import os
import uvicorn
import json
from typing import Dict

load_dotenv()

app = FastAPI()

# Load environment variables
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# Validate environment variables
if not all([SLACK_TOKEN, SLACK_CHANNEL_ID]):
    raise ValueError("❌ Missing Slack credentials in .env file")

# Slack API endpoints
SLACK_MESSAGE_API = "https://slack.com/api/chat.postMessage"
SLACK_GET_UPLOAD_URL_API = "https://slack.com/api/files.getUploadURLExternal"
SLACK_COMPLETE_UPLOAD_API = "https://slack.com/api/files.completeUploadExternal"

SLACK_HEADERS = {
    "Authorization": f"Bearer {SLACK_TOKEN}",
    "Content-Type": "application/json"
}

@app.post("/slack-webhook")
async def send_message(request: Request):
    """Endpoint to send text messages to Slack"""
    try:
        payload = await request.json()
        headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}

        response = requests.post(
            SLACK_MESSAGE_API,
            json={
                "channel": SLACK_CHANNEL_ID,
                "text": payload.get("text", "")
            },
            headers=headers
        )

        if response.status_code == 200 and response.json().get("ok"):
            return {"status": "success", "response": response.json()}
        return {"status": "error", "details": response.text}

    except Exception as e:
        return {"status": "error", "details": str(e)}


@app.post("/upload-from-url")
async def upload_from_url(request: Request):
    """Endpoint to upload a file from a URL to Slack channel"""
    try:
        data = await request.json()
        file_url = data.get("url")

        if not file_url:
            return {"status": "error", "details": "No URL provided"}

        # 1. Download file from URL
        file_response = requests.get(file_url)
        if file_response.status_code != 200:
            return {"status": "error", "details": "Failed to fetch file from URL"}

        file_content = file_response.content
        file_length = len(file_content)
        filename = file_url.split("/")[-1].split("?")[0] or "file_from_url.txt"

        # Debugging: Print out the filename and length
        print(f"Filename: {filename}")
        print(f"Length: {file_length}")
        print(f"Payload: {json.dumps({'filename': filename, 'length': file_length})}")

        # 2. Request an upload URL from Slack using files.getUploadURLExternal
        headers = {
            "Authorization": f"Bearer {SLACK_TOKEN}",
            "Content-Type": "application/json; charset=utf-8"
        }

        payload = {
            "filename": filename,
            "length": str(file_length)  # Ensure length is passed as string
        }

        # Debugging: Check if the payload is correctly serialized
        print(f"Headers: {headers}")
        print(f"Payload: {json.dumps(payload)}")

        upload_url_res = requests.post(
            SLACK_GET_UPLOAD_URL_API,
            headers=headers,
            json=payload  # Ensure we're passing the payload as a JSON object
        )

        # Debugging: Print the upload URL response
        print(f"Upload URL Response: {upload_url_res.text}")

        if not upload_url_res.ok:
            return {"status": "error", "details": upload_url_res.text}

        upload_url_data = upload_url_res.json()
        if not upload_url_data.get("ok"):
            return {"status": "error", "details": upload_url_data}

        upload_url = upload_url_data["upload_url"]
        file_id = upload_url_data["file_id"]

        # 3. Upload the actual file to the upload URL
        upload_response = requests.put(
            upload_url,
            data=file_content,
            headers={"Content-Type": "application/octet-stream"}
        )

        if upload_response.status_code != 200:
            return {"status": "error", "details": "Failed to PUT upload"}

        # 4. Complete the upload process
        complete_res = requests.post(
            SLACK_COMPLETE_UPLOAD_API,
            headers=headers,
            json={
                "files": [{"id": file_id, "title": filename}],
                "channel_id": SLACK_CHANNEL_ID
            }
        )

        if not complete_res.ok or not complete_res.json().get("ok"):
            return {"status": "error", "details": complete_res.text}

        return {"status": "success", "response": complete_res.json()}

    except Exception as e:
        return {"status": "error", "details": str(e)}


#Upload file directly
@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """3 steps file upload endpoint"""
    try:
        # Step 1: Get upload URL
        file_contents = await file.read()
        upload_url_response = requests.post(
            SLACK_GET_UPLOAD_URL_API,
            headers={"Authorization": SLACK_HEADERS["Authorization"]},
            data={
                "filename": file.filename,
                "length": str(len(file_contents))
            }
        )
        
        if not upload_url_response.json().get("ok"):
            return handle_slack_response(upload_url_response)

        upload_data = upload_url_response.json()
        
        # Step 2: Upload file binary
        upload_response = requests.post(
            upload_data["upload_url"],
            files={"file": (file.filename, file_contents)}
        )
        
        if upload_response.status_code != 200:
            return {"status": "error", "details": "File upload failed"}

        # Step 3: Complete upload
        complete_response = requests.post(
            SLACK_COMPLETE_UPLOAD_API,
            headers=SLACK_HEADERS,
            json={
                "files": [{
                    "id": upload_data["file_id"],
                    "title": file.filename
                }],
                "channel_id": SLACK_CHANNEL_ID
            }
        )
        return handle_slack_response(complete_response)
    except Exception as e:
        return {"status": "error", "details": str(e)}

def handle_slack_response(response: requests.Response) -> Dict:
    """Standardize Slack API responses"""
    if response.status_code == 200 and response.json().get("ok"):
        return {
            "status": "success",
            "response": response.json()
        }
    return {
        "status": "error",
        "details": response.text,
        "slack_error": response.json().get("error", "")
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)