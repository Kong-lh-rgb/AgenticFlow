from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()
from langchain.tools import tool
@tool(description="一个用于搜索最新消息的工具，输入一个主题，返回相关的最新消息。")
def search_tool(topic: str):
    tavily_client = TavilyClient(
        api_key=os.getenv('TAVILY_API_KEY')
    )
    query = "关于"+topic+"的最新消息"
    response = tavily_client.search(
        query = query,
        max_results=2,
        include_raw_content=True,
    )
    return response["results"]