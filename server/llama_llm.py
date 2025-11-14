from langchain_community.chat_models import ChatOpenAI
from config import get_secret

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=get_secret("OPENAI_API_KEY"),
)
