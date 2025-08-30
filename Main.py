import streamlit as st
import requests
import base64
from pathlib import Path

# --- Page Configuration ---
st.set_page_config(
    page_title="Insight Engine",
    page_icon="🧠",
    layout="wide"
)

# --- Local CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# --- API URL ---
API_URL = "http://localhost:8000"

# --- Helper function to get image as base64 ---
def get_image_as_base64(path: str) -> str:
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        return None

logo_base64 = get_image_as_base64("logo.png")
LOGO_IMG_TAG = f'<img src="data:image/png;base64,{logo_base64}" width="60">' if logo_base64 else "🧠"

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")
    
    st.subheader("Input URLs")
    urls = [st.text_input(f"URL {i+1}", key=f"url_{i}") for i in range(3)]
    
    if st.button("Process URLs"):
        with st.spinner("Processing URLs..."):
            try:
                response = requests.post(f"{API_URL}/process-urls", json={"urls": [url for url in urls if url]})
                if response.status_code == 200:
                    st.success("URLs processed successfully!")
                    st.session_state.messages = [] 
                else:
                    st.error(f"Error: {response.json().get('detail')}")
            except requests.ConnectionError:
                st.error("Connection Error: Is the API server running?")

    st.subheader("Upload a Document")
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
    
    if st.button("Process File"):
        if uploaded_file:
            with st.spinner("Processing file..."):
                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_URL}/process-file", files=files)
                    if response.status_code == 200:
                        st.success("File processed successfully!")
                        st.session_state.messages = []
                    else:
                        st.error(f"Error: {response.json().get('detail')}")
                except requests.ConnectionError:
                    st.error("Connection Error: Is the API server running?")
        else:
            st.warning("Please upload a file first.")

    st.divider()
    
    # --- NEW: Summarize Button ---
    if st.button("Summarize Content", type="primary"):
        with st.spinner("Generating summary..."):
            try:
                response = requests.post(f"{API_URL}/summarize")
                if response.status_code == 200:
                    summary = response.json().get("summary")
                    # Add summary as an assistant message
                    if "messages" not in st.session_state or not st.session_state.messages:
                        st.session_state.messages = []
                    st.session_state.messages.append({"role": "assistant", "content": f"**Here is a summary of the content:**\n\n{summary}"})
                else:
                    st.error(f"Error: {response.json().get('detail')}")
            except requests.ConnectionError:
                st.error("Connection Error: Is the API server running?")


    if st.button("Clear Session"):
        st.session_state.messages = []
        st.rerun()

# --- Main Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(f"""
    <div class="idle-container">
        <div class="welcome-card">
            <h1>{LOGO_IMG_TAG} Insight Engine</h1>
            <p>Your intelligent assistant for summarizing and querying web articles and documents.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        with st.spinner("Thinking..."):
            try:
                history_for_api = [
                    (st.session_state.messages[i]["content"], st.session_state.messages[i+1]["content"])
                    for i in range(0, len(st.session_state.messages) - 1, 2)
                ]
                
                response = requests.post(
                    f"{API_URL}/ask-question",
                    json={"query": prompt, "chat_history": history_for_api}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Sorry, I couldn't find an answer.")
                    sources = data.get("sources", [])
                    full_response += answer
                    if sources:
                        full_response += "\n\n---\n**Sources:**\n"
                        for source in sources:
                            full_response += f"- {source}\n"
                else:
                    full_response = f"Error: {response.json().get('detail')}"

            except requests.ConnectionError:
                full_response = "Connection Error: Could not connect to the API server."
            
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    if len(st.session_state.messages) == 2:
        st.rerun()
