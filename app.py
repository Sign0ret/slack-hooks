from fastapi import FastAPI, Request
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

if not SLACK_WEBHOOK_URL:
    raise ValueError("❌ Slack webhook URL missing! Check your .env file")

@app.post("/slack-webhook")
async def slack_webhook(request: Request):
    payload = await request.json()
    # Forward the payload to Slack
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    return {"status": "success", "slack_response": response.text}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
