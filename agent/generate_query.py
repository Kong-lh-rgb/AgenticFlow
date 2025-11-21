from graph.content_graph import State
from tools.handle_context import handle_context
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from llm.llm_provider import easy_llm

@dynamic_prompt
def prompt(request: ModelRequest):
    print(request.state)
    question = request.state.get("question")
    print(question)
    extra = request.state.get("context")
    print(extra)
    return f"""
    你是一个帮用户生成搜索 query 的助手。
    补充上下文信息：{extra}
    
    用户的问题是：{question}
    
    请你根据以上信息，生成 3~5 条适合拿去检索资料的查询语句，用 JSON 数组返回，例如：
    ["query1", "query2", "query3"]
    只返回 JSON 数组，不要有其他多余内容。  
    """

agent = create_agent(
    model=easy_llm,
    tools=[],
    middleware=[prompt],
    state_schema=State,
)
#传入prompt的字段是自己定义invoke的字段，我总是想成从全局state里面获取的
def generate_query_node(state:State):
    context = state["context"]
    updated_context = handle_context(context)
    agent_state = {
        "messages": state.get("messages", []) or [],
        "question": state.get("question"),
        "context": updated_context,
    }
    query = agent.invoke(agent_state)
    print(query)
    state['query'] = query
    print(state)
    return state


