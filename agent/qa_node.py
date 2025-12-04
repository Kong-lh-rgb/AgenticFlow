
# agent/qa_node.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from llm.llm_provider import easy_llm
from graph.content_graph import State


class QAOutput(BaseModel):
    answer: str


@dynamic_prompt
def qa_prompt(request: ModelRequest):
    state: State = request.state
    # 优先使用中断回复（user_reply），否则从 messages 里取最后一条 HumanMessage
    user_q = state.get("user_reply")
    if not user_q:
        msgs = state.get("messages") or []
        for m in reversed(msgs):
            if isinstance(m, HumanMessage):
                user_q = getattr(m, "content", None)
                break

    context = state.get("context") or {}
    research = state.get("research_findings") or []
    final_report = state.get("final_report")

    prompt = f"""
你是一个智能助理。根据下面提供的信息和聊天历史，简洁、准确地回答用户的问题或进行闲聊。

【用户问题】
{user_q or "（无明确问题）"}

【已知 context】
{context}

【研究/检索 发现】
{research}

【最终报告（如有）】
{final_report}

【聊天历史（最近在前）】
"""
    msgs = state.get("messages") or []
    for m in msgs[-12:]:
        role = "assistant" if isinstance(m, AIMessage) else "user"
        content = getattr(m, "content", "")
        prompt += f"\n- {role}: {content}"

    prompt += """

输出要求：
只输出一个字段：
{"answer": "<你的回答文字>"} 
不要输出其他任何内容或多余解释。
"""
    return prompt


qa_agent = create_agent(
    model=easy_llm,
    tools=[],
    middleware=[qa_prompt],
    state_schema=State,
    response_format=QAOutput,
)


def qa_node(state: State):
    """基于聊天历史和上下文回答用户问题（闲聊/QA）"""
    result = qa_agent.invoke(state)
    structured = result.get("structured_response")
    answer = ""
    if structured:
        answer = getattr(structured, "answer", "") or ""
    else:
        # 兜底：如果没有 structured_response，尝试取文本响应
        answer = result.get("response") or ""

    # 追加 AIMessage 到会话历史
    messages: List[BaseMessage] = state.get("messages") or []
    messages.append(AIMessage(answer))
    state["messages"] = messages

    # QA 完成，走向结束
    state["next_node"] = "END"
    return state
