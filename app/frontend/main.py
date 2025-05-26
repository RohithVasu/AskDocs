import streamlit as st
from app.frontend.components.document_uploader import DocumentUploader
from app.frontend.components.chat_interface import ChatInterface

# Configure page
st.set_page_config(
    page_title="AskDocs",
    page_icon="📚",
    layout="wide"
)

# Title on main page
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <div style='text-align: center; margin-top: -40px;'>
            <h1>📚 AskDocs</h1>
        </div>
    """, unsafe_allow_html=True)


# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize service and components
uploader = DocumentUploader()
chat = ChatInterface()

uploader.render()

chat.render()

# # Health check
# try:
#     if APIService.check_health():
#         st.sidebar.success("Backend is running")
#     else:
#         st.sidebar.error("Backend is not running")
# except:
#     st.sidebar.error("Backend is not running")
