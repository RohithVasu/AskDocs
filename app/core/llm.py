from langchain.globals import set_llm_cache
from langchain_redis import RedisCache
from langchain.chat_models import init_chat_model
from app.core.settings import settings

# 1️⃣ Set up Redis cache globally (before model initialization)
redis_url = f"redis://{settings.redis.host}:{settings.redis.port}"
redis_cache = RedisCache(redis_url=redis_url)
set_llm_cache(redis_cache)

# 2️⃣ Initialize the model
model = settings.llm.model
model_provider = settings.llm.model_provider
api_key = settings.LLM_API_KEY

llm = init_chat_model(
    model=model,
    model_provider=model_provider,
    api_key=api_key
)