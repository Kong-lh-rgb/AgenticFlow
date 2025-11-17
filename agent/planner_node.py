
from typing import List
from graph.content_graph import State
from llm.llm_provider import easy_llm
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from pydantic import BaseModel



class MissingField(BaseModel):
    field:str
    ask:str
    answer:str | None = None

class PlannerOutput(BaseModel):
    missing: List[MissingField]


@dynamic_prompt
def prompt(request:ModelRequest):
    question = request.state.get("question")
    return (
        f"""你是一个聪明的写报告的助理，你接受用户的问题：{question},
        你的任务是判断用户提供的信息是否足够写出一份合适的报告。
        如果不足请列出所有缺失字段，并且为每个字段提供一个自然的提问语句，
        字段名要简洁明了，提问语句要通顺自然。
        比如"length", "audience", "style", "topic"。
        最后必须按照JSON格式输出missing列表。
        请严格输出如下 JSON 结构：
        {{
          "missing": [
            {{"field": "...", "ask": "..."，"answer",None}},
            ...
          ]
        }}
        不要输出任何解释，不要输出额外文字。"""
    )

agent = create_agent(
    model = easy_llm,
    tools = [],
    middleware = [prompt],
    state_schema=State,
    response_format=PlannerOutput
)

def planner_node(state:State):
    """当前节点识别用户提问中缺少的信息并放到state里"""
    question = state.get("question")
    res = agent.invoke({
        "input": question,
        "question": question
    })
    missing_list = res['structured_response'].missing
    state["user_info"] = [item.model_dump() for item in missing_list]
    if len(missing_list) > 0:
        state["need_ask"] = True
    else:
        state["need_ask"] = False
    state["next_node"] = "ask_user" if state["need_ask"] else "research_node"
    return state
