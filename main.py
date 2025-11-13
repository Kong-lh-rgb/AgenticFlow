from graph.content_graph import State
from langgraph.graph import END,START,StateGraph
from agent.writen_node import writen_node
from agent.critic_node import review_node


def route_function(state:State):
    """判断下一步是写作还是审查"""
    is_final = state["is_final"]
    if is_final:
        return END
    if not is_final:
        return writen_node
#构建图
builder = StateGraph(State)
builder.add_node("writer",writen_node)
builder.add_node("reviewer",review_node)

builder.add_edge(START,"writer")
builder.add_edge("writer","reviewer")
builder.add_conditional_edges(
    "reviewer",
    route_function,
    {
        writen_node:"writer",
        END:END
    }
)

app = builder.compile()

if __name__ == "__main__":
    # 定义初始输入
    initial_input = {
        "topic": "AI Agent",
        "draft": "",
        "content": "这是一份关于AI Agent的资料...",
        "review_notes": [],
        "is_final": False,
    }

    # .stream() 可以让你看到每一步的状态变化
    for step in app.stream(initial_input, {"recursion_limit": 5}):
        node_name = list(step.keys())[0]
        node_output = list(step.values())[0]
        print(f"节点: {node_name}")
        print(f"输出: {node_output}")
        print("-" * 30)

