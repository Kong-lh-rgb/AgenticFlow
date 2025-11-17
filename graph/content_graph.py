from pycparser.c_ast import Continue
from typing_extensions import TypedDict,NotRequired
from langgraph.graph import END,START,StateGraph
from typing import TypedDict, Optional, List, Dict, Any
from langchain.agents import AgentState
from langchain_core.messages import BaseMessage
class State(AgentState):
    task: Optional[str] = None
    context: Dict[str, Any] = {}
    missing: Optional[Dict[str, Any]] = None
    need_ask: bool = False
    messages: List[BaseMessage] = []
    next_node: Optional[str] = None
    user_reply: Optional[str] = None
    question: Optional[str] = None