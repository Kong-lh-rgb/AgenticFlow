from graph.content_graph import State
from pydantic import BaseModel,Field
from typing import Literal
from llm.llm_provider import easy_llm
from langchain.agents import create_agent,AgentState
from langchain.agents.structured_output import ToolStrategy
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.messages import HumanMessage, AIMessage

class RouterOutput(BaseModel):
    intent: Literal["planner_node", "qa_node"]

@dynamic_prompt
def router_prompt(request: ModelRequest):
    question = request.state["question"]
    return f"""
        你是一个意图分类器。你需要判断用户最后一句话的意图。
        
        用户输入：{question}
        
        意图类型：
        1. planner_node：生成类任务（写报告、写总结、写文章、制定计划）。
        2. qa_node：事实类问答（是什么、为什么、多少、怎么做）。
        
        
        只输出其中一个词：
        "planner_node" 或 "qa_node"
        
        不要输出其他内容。
        """


router_agent = create_agent(
    model=easy_llm,
    tools=[],
    middleware=[router_prompt],
    state_schema=State,
    response_format=RouterOutput
)


def router_node(state: State):
    """意图识别：判断用户的最新一句话属于哪个意图"""
    if "messages" not in state:
        state["messages"] = []

    messages = state["messages"]
    question = state.get("question")


    if question:
        messages.append(HumanMessage(content=question))



    latest_text = question if question else (messages[-1].content if messages else "")

    result = router_agent.invoke({
        "messages": messages,
        "question": latest_text
    })

    intent = result["structured_response"].intent

    if intent == "planner_node":
        state["task"] = latest_text

    state["next_node"] = intent
    state["messages"] = messages
    return state


