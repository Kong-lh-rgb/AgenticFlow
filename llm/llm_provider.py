import os
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings


easy_llm = ChatOpenAI(
    base_url='https://api.openai-proxy.org/v1',
    api_key=os.getenv('OPENAI_API_KEY'),
    model = "gpt-4o-mini",
)

smart_llm = ChatOpenAI(
    base_url='https://api.openai-proxy.org/v1',
    api_key=os.getenv('OPENAI_API_KEY'),
    model = "gpt-4o",
)

embedding_models = OpenAIEmbeddings(
    base_url='https://api.openai-proxy.org/v1',
    api_key=os.getenv('OPENAI_API_KEY'),
    model = "text-embedding-3-small"
)