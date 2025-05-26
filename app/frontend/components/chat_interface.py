import streamlit as st
from app.frontend.services.chat import chat
from loguru import logger

class ChatInterface:
    def __init__(self):
        pass

    def render(self) -> None:
        """Render the chat interface component."""
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message("assistant" if message["role"] == "assistant" else "user"):
                st.write(message["content"])
        
        collection_name = st.session_state.get("collection_name", "")
        
        # Chat input
        if question := st.chat_input("Ask a question", key="chat_input"):
            self._handle_chat_message(question, collection_name)

    def _handle_chat_message(self, question: str, collection_name: str) -> None:
        """Handle a new chat message."""
        if not collection_name:
            st.error("Please upload a document first to create a collection")
            return
            
        try:
            # Add user message to history immediately
            st.session_state.chat_history.append({"role": "user", "content": question})
            
            # Get chat response
            response = chat(
                question=question,
                collection_name=collection_name
            )
            
            # Get the answer
            answer = response.get("data", {}).get("answer", "")
            
            # Add assistant message to history
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            
            # Force a rerun to update the UI
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing chat: {str(e)}")
            logger.error(f"Chat error: {str(e)}")
