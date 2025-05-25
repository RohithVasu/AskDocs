import streamlit as st
from typing import List, Dict

from services.api import APIService

class ChatInterface:
    def __init__(self):
        self.api = APIService()

    def render(self) -> None:
        """Render the chat interface component."""
        st.header("Chat with Documents")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message("assistant" if message["role"] == "assistant" else "user"):
                st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("What would you like to know?"):
            self._handle_chat_message(prompt)

    def _handle_chat_message(self, prompt: str) -> None:
        """Handle a new chat message."""
        try:
            with st.spinner("Thinking..."):
                # Get chat response
                response = self.api.chat_with_documents(
                    prompt,
                    st.session_state.chat_history
                )
                
                # Update chat history
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": response["answer"]})
                
                # Rerun to display new messages
                st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
