from fastapi import FastAPI, Request
import requests

app = FastAPI()

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

@app.post("/slack-webhook")
async def slack_webhook(request: Request):
    payload = await request.json()
    # Forward the payload to Slack
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    return {"status": "success", "slack_response": response.text}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
