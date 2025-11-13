from pycparser.c_ast import Continue
from typing_extensions import TypedDict,NotRequired
from langgraph.graph import END,START,StateGraph
class State(TypedDict):
    topic: str  #主题
    draft: str  #草稿
    research_findings: str #资料
    analysis: str    #分析
    review: str #修改意见
    is_final: bool  #是否为最终稿
    count: int #记录写作次数


