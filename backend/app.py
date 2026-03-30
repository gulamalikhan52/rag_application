import streamlit as st
import requests

st.set_page_config(page_title="ChatPDF", page_icon="📄", layout="centered")

st.title("ChatPDF")
st.caption("Upload a PDF and ask questions about it.")

# ── Session state ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False

# ── Sidebar: Upload ──
with st.sidebar:
    st.header("Upload PDF")
    file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if file:
        if st.button("Process PDF"):
            with st.spinner("Processing..."):
                try:
                    res = requests.post(
                        "http://localhost:8000/upload",
                        files={"file": file}
                    )
                    if res.status_code == 200:
                        st.success("PDF ready!")
                        st.session_state.pdf_ready = True
                        st.session_state.messages = []
                    else:
                        st.error("Upload failed.")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.pdf_ready:
        st.info("✅ PDF is active")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Chat ──
if not st.session_state.pdf_ready:
    st.info("👈 Upload and process a PDF from the sidebar to begin.")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask something about your PDF...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    res = requests.get(
                        "http://localhost:8000/ask",
                        params={"q": user_input}
                    )
                    if res.status_code == 200:
                        answer = res.json().get("answer", "No response.")
                    else:
                        answer = "Server error. Check your backend."
                except Exception as e:
                    answer = f"Error: {e}"
            st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
