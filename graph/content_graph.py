from pycparser.c_ast import Continue
from typing_extensions import TypedDict,NotRequired
from langgraph.graph import END,START,StateGraph
from langchain.agents import AgentState
class State(AgentState):
    topic: str  #主题
    draft: str  #草稿
    research_findings: str #资料
    analysis: str    #分析
    review: str #修改意见
    is_final: bool  #是否为最终稿
    count: int #记录写作次数
    next_node:str #router识别后的下一个结点
    question: str #用户的输入
    need_ask: bool #是否需要反问用户
    user_info:list[str] #记录需要用户补充的信息
    ask_message:str
    user_reply:str #用户的回复
