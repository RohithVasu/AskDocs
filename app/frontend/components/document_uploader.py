import streamlit as st
from pathlib import Path
from typing import List

from services.api import APIService

class DocumentUploader:
    def __init__(self):
        self.api = APIService()

    def render(self) -> None:
        """Render the document upload component."""
        st.header("Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=["docx", "xlsx", "csv", "pdf"]
        )
        
        if st.button("Upload") and uploaded_files:
            for file in uploaded_files:
                try:
                    # Save the uploaded file temporarily
                    temp_file = Path("temp") / file.name
                    temp_file.parent.mkdir(exist_ok=True)
                    
                    with open(temp_file, "wb") as f:
                        f.write(file.getvalue())
                    
                    # Upload to backend
                    result = self.api.upload_document(temp_file)
                    st.success(f"Successfully uploaded {file.name}")
                    
                    # Clean up temp file
                    temp_file.unlink()
                except Exception as e:
                    st.error(f"Error uploading {file.name}: {str(e)}")
