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

# Section 2: File Upload
with st.expander("📁 Upload File", expanded=True):
    with st.form("upload_form"):
        uploaded_file = st.file_uploader(
            "Choose a file to upload to Slack:",
            type=['png', 'jpg', 'pdf'],
            accept_multiple_files=False
        )
        
        if st.form_submit_button("⬆️ Upload File"):
            if uploaded_file is not None:
                # Prepare the file for upload
                file_bytes = uploaded_file.getvalue()
                
                # Prepare the request data
                files = {"file": (uploaded_file.name, file_bytes)}
                
                # Show upload progress
                with st.spinner(f"Uploading {uploaded_file.name}..."):
                    try:
                        response = requests.post(
                            f"{API_BASE}/upload-file",
                            files=files
                        )
                        
                        if response.json().get("status") == "success":
                            st.success("✅ File uploaded successfully!")
                            st.balloons()
                            
                        else:
                            st.error(f"❌ Upload failed: {response.json().get('details', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"🚨 An error occurred: {str(e)}")
            else:
                st.warning("⚠️ Please select a file to upload!")

# Section 3: Upload file via URL 
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
                    st.success("✅ File successfully uploaded from URL!")
                    st.balloons()
                    #st.json(response.json().get("response", {}))
                else:
                    st.error(f"URL upload failed: {response.json().get('details', 'Unknown error')}")
            else:
                st.warning("Please enter a valid URL!")

# Footer
st.markdown("---")
st.caption("⚡ Powered by Streamlit & FastAPI | 🚀 Slack Integration")
