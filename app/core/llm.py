from langchain_groq import ChatGroq
from app.core.config import settings

def get_llm():
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model="deepseek-r1-distill-llama-70b",  # you can change model
        temperature=0.7
    )