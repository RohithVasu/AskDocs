import streamlit as st

from app.frontend.services.api_service import APIService

class HealthCheck:
    def __init__(self):
        self.api_service = APIService()

    def render(self) -> bool:
        """Render the health check component."""
        try:
            if self.api_service.check_health():
                return True
            else:
                return False
        except Exception as e:
            st.sidebar.error(f"Failed to check health: {str(e)}")