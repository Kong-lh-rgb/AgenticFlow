from graph.content_graph import State
from langgraph.graph import END,START,StateGraph
from agent.writen_node import writen_node
from agent.critic_node import review_node
from agent.retriever_node import retriever_node
from agent.indexing_node import put_in_db
from agent.research_node import search_node
from agent.planner_node import planner_node
from agent.router_node import router_node
from agent.qa_node import qa_node

def router(state:State):
    """路由节点，决定下一步走向"""
    next_node = state.get("next_node")
    if next_node == "qa_node":
        return "qa_node"
    if next_node == "planner_node":
        return "planner_node"


def route_function(state:State):
    """判断下一步是写作还是审查"""
    is_final = state["is_final"]
    if is_final:
        return "over"
    if not is_final:
        return "re_write"
#构建图
builder = StateGraph(State)
builder.add_node("router",router_node)
builder.add_node("writer",writen_node)
builder.add_node("researcher",search_node)
builder.add_node("indexer",put_in_db)
builder.add_node("planner",planner_node)
builder.add_node("retriever",retriever_node)
builder.add_node("reviewer",review_node)
builder.add_node("qa",qa_node)

builder.add_edge(START,"router")
builder.add_edge("planner","researcher")
builder.add_edge("researcher","indexer")
builder.add_edge("indexer","retriever")
builder.add_edge("retriever","writer")
builder.add_edge("writer","reviewer")
builder.add_edge("qa",END)

builder.add_conditional_edges(
    "router",
    router,
    {
        "qa_node":"qa",
        "planner_node":"planner"
    }
)

builder.add_conditional_edges(
    "reviewer",
    route_function,
    {
        "re_writer":"writer",
        "over":END
    }
)

app = builder.compile()


