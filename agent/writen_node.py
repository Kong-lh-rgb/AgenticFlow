#根据提供的资料撰写报告
from graph.content_graph import State
from langchain.agents import create_agent
from prompts.prompt import WRITEN_PROMPTS
from llm.llm_provider import easy_llm
def writen_agent(topic:str,draft:str,content:str,review_notes:list[str]) -> str:
    chain = WRITEN_PROMPTS | easy_llm
    response = chain.invoke({
        "topic": topic,
        "content": content,
        "draft": draft,
        "review_notes": "\n".join(review_notes)
    })
    return response.content
def writen_node(state:State):
    """写作结点"""
    print("进入写作节点")
    topic = state["topic"]
    draft = state["draft"]
    content = state["content"]
    review_notes = state["review_notes"]
    if review_notes:
        print("根据修改意见进行修改")
        new_draft = writen_agent(topic,draft,content,review_notes)
    else:
        print("进行初稿写作")
        new_draft = writen_agent(topic, content, [])
    return {"draft": new_draft, "is_final": False} # 每次写完都默认不是最终稿
