from dotenv import load_dotenv
load_dotenv()
import re
# from dataclasses import dataclass
# from langchain.agents import create_agent
# from langchain.agents.middleware import dynamic_prompt, ModelRequest
# from llm.llm_provider import easy_llm
# from tools.search_tool import search_tool
# from prompts.prompt import research_prompt
from graph.content_graph import State
#
# @dataclass
# class ResearchContext:
#     topic: str
#
# def research_node(state: State):
#     """执行研究任务"""
#     model = easy_llm
#     tools = [search_tool]
#
#     agent = create_agent(
#         model=model,
#         tools=tools,
#         middleware=[research_prompt],
#         context_schema=ResearchContext,
#     )
#
#     topic = state["topic"]
#
#     result = agent.invoke(
#         {"input": "请围绕主题进行研究并总结要点。"},
#         context=ResearchContext(topic=topic),
#     )
#
#     return result
from tavily import TavilyClient
import os

def clean_text(text: str) -> str:
    """
    清理文本：
    - 去掉 Markdown 图片 ![](...)
    - 去掉 Markdown 链接 [text](url)
    - 去掉 HTML 标签
    - 去掉标题 Markdown #、## 等
    - 去掉多余空行和首尾空格
    """
    # 去掉 Markdown 图片
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    # 去掉 Markdown 链接，只保留链接文字
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    # 去掉 Markdown 标题
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    # 去掉 HTML 标签
    text = re.sub(r"<.*?>", "", text)
    # 去掉多余空白行
    text = re.sub(r"\n\s*\n", "\n", text)
    # 去掉首尾空格
    text = text.strip()
    return text



def search_node(state:State):
    # """搜索资料清洗数据"""
    # tavily_client = TavilyClient(
    #     api_key=os.getenv('TAVILY_API_KEY')
    # )
    # query = state.get("question")
    # response = tavily_client.search(
    #     query = query,
    #     max_results=2,
    #     include_raw_content=True,
    # )
    # results = []
    # for item in response["results"]:
    #     raw = item.get("raw_content", "")
    #     cleaned = clean_text(raw)
    #     results.append(cleaned)
    # state["research_findings"] = "\n\n".join(results)
    # return state["research_findings"]
    print(state)

