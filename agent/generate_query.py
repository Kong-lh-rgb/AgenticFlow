from graph.content_graph import State
from tools.handle_context import handle_context
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from llm.llm_provider import easy_llm
from pydantic import BaseModel
import json

class QueryOutput(BaseModel):
    query: list[str]


@dynamic_prompt
def prompt(request: ModelRequest):
    question = request.state.get("question")
    extra = request.state.get("context")
    return f"""
你是一个帮用户生成搜索 query 的助手。
补充上下文信息：{extra}

用户的问题是：{question}

请你根据以上信息，生成 3~5 条适合拿去检索资料的查询语句。
请只返回一个 JSON 对象，格式必须严格如下（不要输出多余文字）：
{{"query": ["query1", "query2", "query3"]}}
"""


agent = create_agent(
    model=easy_llm,
    tools=[],
    middleware=[prompt],
    state_schema=State,
    response_format=QueryOutput
)


def generate_query_node(state: State):
    # 1) 处理 context
    updated_context = handle_context(state.get("context") or {})

    # 2) 只把 prompt 会用到的字段传给 agent（避免把整坨 state 传进去越来越大）
    agent_state = {
        "messages": state.get("messages") or [],
        "question": state.get("question"),
        "context": updated_context,
    }

    # 3) 调 agent
    res = agent.invoke(agent_state)

    # 4) 提取 query（只落一个 List[str] 到 state["query"]，别把整坨 res 塞进去）
    queries: list[str] = []

    # 情况 A：res 就是 QueryOutput（有些版本会直接返回结构化对象）
    if hasattr(res, "query"):
        queries = list(res.query)

    # 情况 B：res 是 dict（更常见：包含 structured_response / output / messages）
    elif isinstance(res, dict):
        sr = res.get("structured_response")
        if sr is not None and hasattr(sr, "query"):
            queries = list(sr.query)
        else:
            out = res.get("output", "")
            # 兜底：如果 output 是字符串 JSON，就解析一下
            if isinstance(out, str) and out.strip():
                try:
                    obj = json.loads(out)
                    if isinstance(obj, dict) and isinstance(obj.get("query"), list):
                        queries = obj["query"]
                    elif isinstance(obj, list):
                        queries = obj
                except Exception:
                    pass

        # 如果 agent 返回了 messages，你可以选择同步回主 state（推荐）
        if "messages" in res and isinstance(res["messages"], list):
            state["messages"] = res["messages"]

    # 5) 写回主 state（类型正确）
    state["context"] = updated_context
    state["query"] = queries
    state["next_node"] = "research_node"  # 让图流转到搜索节点

    return state
