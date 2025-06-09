import streamlit as st
from app.frontend.components.document_uploader import DocumentUploader
from app.frontend.components.chat_interface import ChatInterface
from app.frontend.components.health_check import HealthCheck
import time

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

# Check if backend is healthy
if 'health_check_passed' not in st.session_state:
    st.session_state.health_check_passed = False

if not st.session_state.health_check_passed:
    with st.spinner('Connecting to AskDocs service...'):
        # Try health check for up to 120 seconds
        max_attempts = 120
        for i in range(max_attempts):
            health_check = HealthCheck()
            if health_check.render():
                st.session_state.health_check_passed = True
                break
            time.sleep(1)

# Only render components if health check passed
if st.session_state.health_check_passed:
    uploader.render()
    chat.render()
else:
    st.error('Failed to connect to AskDocs service. Please try again later.')
