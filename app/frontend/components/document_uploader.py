import streamlit as st
from pathlib import Path
from app.frontend.services.upload import upload_document
from loguru import logger

class DocumentUploader:
    def __init__(self):
        pass

    def render(self) -> None:
        """Render the document upload component."""
        st.sidebar.subheader("Upload Document")
        
        # Display file upload with a smaller width
        uploaded_file = st.sidebar.file_uploader(
            "Choose a file",
            accept_multiple_files=False,
            type=["docx", "pdf", "ppt", "pptx", "txt", "csv"],
            key="document_uploader"
        )
        
        # Upload button with smaller size
        if st.sidebar.button("Upload", use_container_width=True) and uploaded_file:
            try:
                # Save the uploaded file temporarily
                temp_file = Path("temp") / uploaded_file.name           
                temp_file.parent.mkdir(exist_ok=True)
                
                with open(temp_file, "wb") as f:
                    f.write(uploaded_file.getvalue())

                # Upload document and get collection name
                collection_name = upload_document(temp_file)
                st.session_state.collection_name = collection_name
                
                # Show success message with collection name
                if collection_name:
                    st.sidebar.success(f"Successfully uploaded {uploaded_file.name} to collection: {collection_name}")
                else:
                    st.sidebar.success(f"Successfully uploaded {uploaded_file.name}")
                
                # Clean up temp file
                temp_file.unlink()
            except Exception as e:
                st.sidebar.error(f"Failed to upload document. Please try again.")
