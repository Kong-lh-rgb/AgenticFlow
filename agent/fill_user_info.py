from langchain_core.messages import HumanMessage

from graph.content_graph import State
from llm.llm_provider import easy_llm

def fill_user_info_node(state:State):
    user_info = state.get("user_info", [])
    user_reply = state.get("user_reply", "")
    fields = "\n".join([f"- {u['field']}" for u in user_info])

    prompt = f"""
    你是一个信息抽取助手。

    以下是需要填写的字段：
    {fields}

    用户的补充回答是：
    {user_reply}

    请从用户的回答中提取字段对应的值，以 JSON 格式返回，缺失的字段不要填。
    格式如下：
    {{
      "字段1": "值",
      "字段2": "值"
    }}
    """

    result = easy_llm.invoke([HumanMessage(content=prompt)])

    # 解析 result 成 dict（你模型应该返回 JSON）
    import json
    extracted = json.loads(result.content)

    for ui in user_info:
        field = ui["field"]
        if field in extracted:
            ui["answer"] = extracted[field]

    state["user_info"] = user_info
    return state