from langchain_openai import ChatOpenAI
from config import GROQ_API_KEY

llm = ChatOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    model="llama-3.3-70b-versatile",
    temperature=0.1)