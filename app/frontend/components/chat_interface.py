import streamlit as st
import time
from app.frontend.services.api_service import APIService
from loguru import logger


class ChatInterface:
    def __init__(self):
        self.api_service = APIService()
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "pending_question" not in st.session_state:
            st.session_state.pending_question = None

    def render(self) -> None:
        """Render the chat interface component."""
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message("assistant" if message["role"] == "assistant" else "user"):
                st.markdown(message["content"])

        collection_name = st.session_state.get("collection_name", "")

        # Handle pending question (process & stream response)
        if st.session_state.pending_question and collection_name:
            question = st.session_state.pending_question
            st.session_state.pending_question = None  # clear it

            # Add placeholder for assistant message
            st.session_state.chat_history.append({"role": "assistant", "content": ""})

            try:
                response = self.api_service.chat(
                    question=question,
                    collection_name=collection_name
                )
                answer = response.get("data", {}).get("answer", "")

                full_response = ""
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    for char in answer:
                        full_response += char
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.02)
                    message_placeholder.markdown(full_response)

                st.session_state.chat_history[-1]["content"] = full_response

            except Exception as e:
                st.error("Failed to get chat response.")
                logger.error(f"Chat error: {e}")

        # Chat input
        question = st.chat_input("Ask a question")
        if question:
            if not collection_name:
                st.error("No document uploaded, please upload a document.")
                return

            # Add user message and defer processing
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.session_state.pending_question = question
            st.rerun()  # show user message immediately