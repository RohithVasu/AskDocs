from langchain.chat_models import init_chat_model

from app.core.settings import settings

model = settings.llm.model
model_provider = settings.llm.model_provider
api_key = settings.LLM_API_KEY

llm = init_chat_model(model=model, model_provider=model_provider, api_key=api_key)