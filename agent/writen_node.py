#根据提供的资料撰写报告
from graph.content_graph import State
from langchain.agents import create_agent
from prompts.prompt import WRITEN_PROMPTS
from llm.llm_provider import easy_llm
def writen_node(state:State):
    """写作结点"""
