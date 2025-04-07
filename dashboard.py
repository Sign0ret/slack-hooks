import streamlit as st
import requests

API_URL = "http://localhost:8000/slack-webhook"

st.title("Streamlit + Slack Integration")

# Input form to send a message to Slack
with st.form("slack_form"):
    message = st.text_input("Enter your message for Slack:")
    submit_button = st.form_submit_button("Send to Slack")

    if submit_button and message:
        payload = {"text": message}
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            st.success("Message sent to Slack!")
        else:
            st.error("Failed to send message.")

