import streamlit as st
from components.document_uploader import DocumentUploader
from components.chat_interface import ChatInterface
from services.api import APIService

# Configure page
st.set_page_config(
    page_title="Document Chat",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize components
uploader = DocumentUploader()
chat = ChatInterface()

# Page layout
st.title("📚 Document Chat")

doc_upload_col, chat_col = st.columns([1, 2])

with doc_upload_col:
    uploader.render()

with chat_col:
    chat.render()

# Health check
try:
    if APIService.check_health():
        st.sidebar.success("Backend is running")
    else:
        st.sidebar.error("Backend is not running")
except:
    st.sidebar.error("Backend is not running")
