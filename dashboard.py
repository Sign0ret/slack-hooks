import streamlit as st
import requests

# Configuration
API_BASE = "http://localhost:8000"
st.set_page_config(page_title="Slack Integration Dashboard", layout="wide")

# Custom CSS for better spacing
st.markdown("""
<style>
    .stExpander {
        margin: 15px 0;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("📤 Slack Integration Dashboard")

# Section 1: Send Message
with st.expander("💬 Send Text Message", expanded=True):
    with st.form("message_form"):
        message = st.text_area(
            "Compose your message:",
            height=150,
            placeholder="Type your message here..."
        )
        
        if st.form_submit_button("🚀 Send Message"):
            if message.strip():
                response = requests.post(
                    f"{API_BASE}/slack-webhook",
                    json={"text": message}
                )
                
                if response.json().get("status") == "success":
                    st.success("Message successfully sent to Slack!")
                    st.balloons()
                else:
                    st.error(f"❌ Failed to send message: {response.json().get('details', 'Unknown error')}")
            else:
                st.warning("Please enter a message before sending!")

# Section 3: Upload from URL
with st.expander("🌐 Upload from URL", expanded=True):
    with st.form("url_form"):
        file_url = st.text_input(
            "Enter file URL:",
            placeholder="https://example.com/file.pdf"
        )
        
        if st.form_submit_button("🔗 Upload from URL"):
            if file_url.strip():
                response = requests.post(
                    f"{API_BASE}/upload-from-url",
                    json={"url": file_url}
                )
                
                if response.json().get("status") == "success":
                    st.success("File successfully uploaded from URL!")
                    st.json(response.json().get("response", {}))
                else:
                    st.error(f"URL upload failed: {response.json().get('details', 'Unknown error')}")
            else:
                st.warning("Please enter a valid URL!")

# Footer
st.markdown("---")
st.caption("⚡ Powered by Streamlit & FastAPI | 🚀 Slack Integration")
