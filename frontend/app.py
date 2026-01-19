import streamlit as st
import requests

API_CHAT = "http://localhost:8000/chat"
API_UPLOAD = "http://localhost:8000/upload"

st.set_page_config(page_title="RAG Chat", layout="centered")
st.title("📄 Chat with your PDFs")


st.subheader("Upload PDF")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    if st.button("Process PDF"):
        files = {"file": uploaded_file}
        with st.spinner("Uploading and indexing..."):
            r = requests.post(API_UPLOAD, files=files)
            r.raise_for_status()
        st.success("PDF uploaded and indexed!")


st.divider()

st.subheader("Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


user_input = st.chat_input("Ask something about your PDFs...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        r = requests.post(API_CHAT, json={"question": user_input})
        r.raise_for_status()
        answer = r.json()["answer"]

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

