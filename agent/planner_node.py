from typing import List
from graph.content_graph import State
from llm.llm_provider import easy_llm
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from pydantic import BaseModel
from typing import Optional

class MissingField(BaseModel):
    field:str
    question:str


class PlannerOutput(BaseModel):
    need_ask:bool
    missing: Optional[MissingField] = None


@dynamic_prompt
def prompt(request:ModelRequest):
    task = request.state.get("task")#获取当前任务
    context = request.state.get("context",{})#获取完成当前任务要用到的信息
    return f"""
    你是一个经验丰富的信息规划智能体（Dynamic Planner Agent）。

    你的任务是：
    根据用户的原始任务（task）和已经收集到的信息（context），
    判断当前是否需要向用户提一个关键问题，以便最终完成任务。
    ------------------------
    【任务说明】
    {task}

    【当前已知信息 context】
    {context}
    ------------------------
    【你的工作流程】
    1. 分析 task，判断task描述是否具备写一篇报告足够的信息，若不足则分析完成该任务所需要的关键参数有哪些。
    2. 检查哪些参数已经在 context 中被填充。
    3. 如果所有关键参数都已具备，则输出：
       {{
         "need_ask": false,
         "missing": null
       }}

    4. 如果缺少关键信息，只选择“当前最重要的那一项”提出问题，输出：
       {{
         "need_ask": true,
         "missing": {{
            "field": "缺少的字段名（英文简短）",
            "question": "向用户提问的自然语言问题"
         }}
       }}

    5. 绝对不要列出多个字段，一次只问一个关键字段。

    ------------------------
    【输出要求（非常重要）】
    - 必须严格输出 JSON
    - 必须符合如下结构：
      {{
        "need_ask": <true|false>,
        "missing": {{
            "field": "<str>",
            "question": "<str>"
        }} | null
      }}
    - 不要输出额外解释内容
    开始分析并输出 JSON：
    """

planner_agent = create_agent(
    model = easy_llm,
    tools = [],
    middleware = [prompt],
    state_schema=State,
    response_format=PlannerOutput
)

def planner_node(state: State):
    task = state["task"]
    context = state.get("context", {})
    messages = state.get("messages", [])
    res = planner_agent.invoke({
        "task": task,
        "context": context,
        "messages": messages
    })

    out: PlannerOutput = res["structured_response"]

    state["need_ask"] = out.need_ask
    state["missing"] = out.missing.model_dump() if out.missing else None

    # 如果需要问问题 → 跳到 ask_node.py
    if out.need_ask:
        state["next_node"] = "ask_node"
    else:
        state["next_node"] = "research_node"

    return state


