from fastapi import FastAPI, Request, UploadFile, File, Body
import requests
from dotenv import load_dotenv
import os
import uvicorn
import json
from typing import Dict
from urllib.request import urlopen
from io import BytesIO

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

@app.post("/upload-from-url")
async def upload_from_url(payload: Dict = Body(...)):
    """Endpoint to upload a file from URL to Slack"""
    try:
        url = payload.get("url")
        if not url:
            return {"status": "error", "details": "URL is required"}
        
        # Step 1: Download the file
        with urlopen(url) as response:
            file_bytes = response.read()
            filename = url.split('/')[-1] or "downloaded_file"
            
            file = UploadFile(
                filename=filename,
                file=BytesIO(file_bytes),
                size=len(file_bytes)
            )
            
            # Step 2: Reuse the existing upload endpoint
            return await upload_file(file)
            
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