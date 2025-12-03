import streamlit as st
import requests
import os


st.set_page_config(
    page_title="🧠Insight Engine",
    layout="wide"
)


API_URL = "http://127.0.0.1:8000"


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


local_css("style.css")


with st.sidebar:
    st.header("Configuration")
    
    st.subheader("Input URLs")
    urls = []
    for i in range(3):
        url = st.text_input(f"URL {i+1}", key=f"url_{i}", placeholder="https://example.com")
        if url:
            urls.append(url)

    if st.button("Process URLs", key="process_urls"):
        if not any(urls):
            st.warning("Please enter at least one URL.")
        else:
            with st.spinner("Processing..."):
                try:
                    response = requests.post(f"{API_URL}/process-urls", json={"urls": urls})
                    if response.status_code == 200:
                        st.success("URLs processed successfully!")
                        st.session_state.processed = True
                        if 'messages' in st.session_state:
                            st.session_state.messages = [{"role": "assistant", "content": "I've processed the new documents. How can I help?"}]
                    else:
                        st.error(f"Error: {response.json().get('detail')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: Could not connect to the API. Is it running?")

    st.subheader("Upload a Document")
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])

    if st.button("Process File", key="process_file"):
        if uploaded_file is None:
            st.warning("Please upload a file first.")
        else:
            with st.spinner("Processing..."):
                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_URL}/process-file", files=files)
                    if response.status_code == 200:
                        st.success(f"File '{uploaded_file.name}' processed successfully!")
                        st.session_state.processed = True
                        if 'messages' in st.session_state:
                             st.session_state.messages = [{"role": "assistant", "content": "I've processed the new document. How can I help?"}]
                    else:
                        st.error(f"Error: {response.json().get('detail')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: Could not connect to the API.")

    st.subheader("Actions")
    if st.button("Summarize Content", key="summarize"):
        if 'processed' not in st.session_state or not st.session_state.processed:
            st.warning("Please process some documents first.")
        else:
            with st.spinner("Generating summary..."):
                try:
                    response = requests.post(f"{API_URL}/summarize", json={})
                    if response.status_code == 200:
                        summary = response.json()
                        st.session_state.messages.append({"role": "assistant", "content": f"**Summary of the content:**\n\n{summary['answer']}"})
                    else:
                        st.error(f"Error: {response.json().get('detail')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: Could not connect to the API.")

    if st.button("Clear Session", key="clear_session"):
        st.session_state.messages = []
        st.session_state.processed = False
        st.rerun()




if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed" not in st.session_state:
    st.session_state.processed = False


if not st.session_state.messages:
    st.markdown(
        """
        <div class="idle-wrapper">
          <div class="welcome-card">
            <div class="icon"></div>
            <h1>🧠Insight Engine</h1>
            <p class="subtitle">Your intelligent assistant for summarizing and querying web articles and documents.</p>
            <div class="search-slot"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    prompt = st.chat_input("Ask a question about your documents…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()


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
            message_placeholder.markdown("Thinking...")
            
            if not st.session_state.processed:
                message_placeholder.error("I can't answer yet. Please process some URLs or a file first using the sidebar.")
            else:
                try:
                    history = []
                    for msg in st.session_state.messages[:-1]: 
                        if msg["role"] == "user":
                            try:
                                assistant_msg = st.session_state.messages[st.session_state.messages.index(msg) + 1]['content']
                                history.append((msg['content'], assistant_msg))
                            except (IndexError, KeyError):
                                pass

                    response = requests.post(
                        f"{API_URL}/ask-question", 
                        json={"query": prompt, "chat_history": history}
                    )

                    if response.status_code == 200:
                        result = response.json()
                        answer = result['answer']
                        sources = result['sources']
                        
                        full_response = answer
                        if sources and sources[0] not in ["Conversational AI", "Summary of all processed documents"]:
                            full_response += "\n\n**Sources:**\n"
                            for source in sources:
                                full_response += f"- {source}\n"
                        
                        message_placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    else:
                        error_detail = response.json().get('detail')
                        message_placeholder.error(f"Error from API: {error_detail}")
                        st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_detail}"})

                except requests.exceptions.RequestException as e:
                    message_placeholder.error(f"Connection error: Could not connect to the API.")
                    st.session_state.messages.append({"role": "assistant", "content": "Error: Could not connect to the API."})

