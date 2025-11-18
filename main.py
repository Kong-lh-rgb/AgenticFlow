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
from langgraph.checkpoint.memory import InMemorySaver
from agent.ask_node import ask_node
from agent.fill_node import fill_node
from agent.validator_node import validator_node



def router(state:State):
    """路由节点，决定下一步走向"""
    next_node = state.get("next_node")
    if next_node == "qa_node":
        return "qa_node"
    elif next_node == "planner_node":
        return "planner_node"

def router_after_planner(state:State):
    next_node = state.get("next_node")
    if next_node == "research_node":
        return "research_node"
    elif next_node == "ask_node":
        return "ask_node"

def route_function(state:State):
    """判断下一步是写作还是审查"""
    is_final = state["is_final"]
    if is_final:
        return "over"
    if not is_final:
        return "re_write"

def router_after_fii(state:State):
    next_node = state.get("next_node")
    if next_node == "fill_node":
        return "fill_node"
    else:
        return "validator_node"

def router_after_validator(state:State):
    next_node = state.get("next_node")
    if next_node == "ask_node":
        return "ask_node"
    elif next_node == "research_node":
        return "research_node"
#构建图
builder = StateGraph(State)
builder.add_node("router",router_node)
builder.add_node("ask",ask_node)
builder.add_node("fill",fill_node)
builder.add_node("validator",validator_node)
builder.add_node("writer",writen_node)
builder.add_node("researcher",search_node)
builder.add_node("indexer",put_in_db)
builder.add_node("planner",planner_node)
builder.add_node("retriever",retriever_node)
builder.add_node("reviewer",review_node)
builder.add_node("qa",qa_node)

builder.add_edge(START,"router")
# builder.add_edge("planner","ask")

builder.add_edge("ask","fill")
# builder.add_edge("fill","validator")

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
    "planner",
    router_after_planner,
    {
        "research_node":"researcher",
        "ask_node":"ask"
    }
)

builder.add_conditional_edges(
    "fill",
    router_after_fii,
    {
        "fill_node":"fill",
        "validator_node":"validator"
    }
)

builder.add_conditional_edges(
    "validator",
    router_after_validator,
    {
        "ask_node": "ask",
        "research_node":"researcher"
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

memory = InMemorySaver()
app = builder.compile(checkpointer=memory)

# app = builder.compile()

