from graph.content_graph import State
from langgraph.types import interrupt
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.agents import create_agent
from llm.llm_provider import easy_llm
from pydantic import BaseModel
from langchain_core.messages import AIMessage,HumanMessage

class AskOutput(BaseModel):
    ask: str


@dynamic_prompt
def ask_prompt(request: ModelRequest):
    missing = request.state.get("missing")
    task = request.state.get("task")
    context = request.state.get("context")

    return f"""
        你是一个智能助理，正在帮助用户完成任务：
        
        【任务】
        {task}
        
        【当前已知信息 context】
        {context}
        
        当前缺失的关键信息是字段：{missing["field"]}
        
        你需要向用户提出下面这个问题：
        "{missing["question"]}"
        
        【你的目标】
        1. 直接向用户提出这个问题。
        2. 用自然、有礼貌的语言表达。
        
        【输出要求】
        只输出一个字段：
        {{"ask": "<你要问用户的话>"}}
        
        不要输出其他任何内容。
        
        请输出 JSON：
        """

ask_agent = create_agent(
    model=easy_llm,
    tools=[],
    middleware=[ask_prompt],
    state_schema=State,
    response_format=AskOutput
)

def ask_node(state: State):
    """负责向用户提问，并进入 interrupt"""

    # 取出 planner 填好的 missing 字段
    missing = state["missing"]

    # 用 ask_agent 生成自然语言问句
    messages = state["messages"]
    result = ask_agent.invoke(state)
    ask_text = result["structured_response"].ask
    messages.append(AIMessage(ask_text))

    # interrupt 内容给 run_graph 展示
    user_reply = interrupt(ask_text)
    #中断后继续执行这个代码，判断用户输入的类型交给下一个代码
    state["user_reply"] = user_reply
    print(state)
    return state