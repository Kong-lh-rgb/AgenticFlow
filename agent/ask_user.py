from graph.content_graph import State
from langgraph.types import interrupt

#需要用户输入信息，告诉用户需要什么，并且暂停图的执行
def ask_node(state:State):
    """向用户提问以获取缺失的信息"""
    # missing = state.get("user_info", [])
    missing = [x for x in state["user_info"] if x["answer"] is None]
    text = " "
    for m in missing:
        text += f"- {m['ask']}\n"
    # state["ask_message"] = text
    state["next_node"] = "user"
    # user_info = []
    # state["user_info"] = user_info
    user_need = interrupt({
        "instruction":"请补充以下信息：、n",
        "content": text,
    })
    return {"user_reply": user_need}