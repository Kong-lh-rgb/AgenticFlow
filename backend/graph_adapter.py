from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.types import Command  # interrupt/resume 关键

# 这里假设你已经把 app = builder.compile(checkpointer=...) 放在某处可导入
from graph_runner import app  # 你按你的实际路径改：能 import 到 compiled graph 就行


# 简单版：用内存标记某个 session 是否正在等待用户回复（开发期够用）
# 如果你 uvicorn --reload 或重启，会丢；想稳就用“数据库字段版”（下面也给了思路）
_WAITING = set()


def _extract_interrupt_text(out_state: Dict[str, Any]) -> Optional[str]:
    """
    LangGraph interrupt 的 payload 会在 out_state['__interrupt__'] 里返回
    可能是一个 Interrupt 对象列表：Interrupt(value=...)
    """
    intr = out_state.get("__interrupt__")
    if not intr:
        return None

    # intr 通常是 list[Interrupt]
    first = intr[0] if isinstance(intr, list) and intr else intr

    # Interrupt 对象一般有 .value
    payload = getattr(first, "value", first)

    # 你也可以在 interrupt() 里传 dict，例如 {"type":"ask","question":"..."}
    if isinstance(payload, dict):
        return payload.get("question") or payload.get("text") or str(payload)

    return str(payload)


def _extract_last_ai_message(messages: Any) -> Optional[str]:
    if not messages or not isinstance(messages, list):
        return None
    for m in reversed(messages):
        if isinstance(m, AIMessage):
            return m.content
    return None


def run_agentic_flow(session_id: int, user_message: str) -> Dict[str, Any]:
    """
    返回结构：
    - assistant_message: 给前端展示的一句话（可能是追问，也可能是正常回复）
    - report: {"title":..., "content":...} 或 None
    - interrupted: bool（是否在等待用户补充信息）
    """
    config = {"configurable": {"thread_id": str(session_id)}}

    # 如果上一次已经 interrupt 了，本次就必须用 Command(resume=...) 续跑
    if session_id in _WAITING:
        out_state = app.invoke(Command(resume=user_message), config=config)
        _WAITING.discard(session_id)
    else:
        # 新一轮对话：把用户消息作为 HumanMessage 塞进 state.messages
        out_state = app.invoke({"messages": [HumanMessage(content=user_message)]}, config=config)

    # 1) 先看是不是触发了 interrupt（也就是“AI 在问你要主题是什么”这种）
    question = _extract_interrupt_text(out_state)
    if question:
        _WAITING.add(session_id)
        return {"assistant_message": question, "report": None, "interrupted": True}

    # 2) 没 interrupt：正常产出（你 State 里叫 final_report）
    report_text = out_state.get("final_report")
    if report_text:
        return {
            "assistant_message": "报告已生成。",
            "report": {"title": "report", "content": report_text},
            "interrupted": False,
        }

    # 3) 没 final_report：就从 messages 里抓最后一句 AIMessage
    last_ai = _extract_last_ai_message(out_state.get("messages"))
    if last_ai:
        return {"assistant_message": last_ai, "report": None, "interrupted": False}

    # 兜底
    return {
        "assistant_message": "（没有拿到 interrupt / final_report / AIMessage，请检查各节点是否往 state.messages 追加 AIMessage，或是否在 interrupt() 里传了 payload）",
        "report": None,
        "interrupted": False,
    }
