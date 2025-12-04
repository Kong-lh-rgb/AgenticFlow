# backend/graph_adapter.py
from typing import Any, Dict, Optional, Tuple

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command

from graph_runner import app  # 你自己的 compiled graph: app = builder.compile(...)

# 开发期防重复（uvicorn --reload 会丢；想稳就把 run_id 写进 reports 表并做唯一约束）
_SAVED: set[Tuple[int, int]] = set()  # (session_id, run_id)


def _extract_interrupt_text(out_state: Dict[str, Any]) -> Optional[str]:
    intr = out_state.get("__interrupt__")
    if not intr:
        return None
    first = intr[0] if isinstance(intr, list) and intr else intr
    payload = getattr(first, "value", first)
    if isinstance(payload, dict):
        return payload.get("question") or payload.get("text") or str(payload)
    return str(payload)


def _extract_last_ai_message(messages: Any) -> Optional[str]:
    if not isinstance(messages, list):
        return None
    for m in reversed(messages):
        if isinstance(m, AIMessage):
            return m.content
    return None


def _guess_report_title(out_state: Dict[str, Any]) -> str:
    ctx = out_state.get("context") or {}
    topic = ctx.get("topic")
    if topic:
        return f"{topic}-报告"
    task = out_state.get("task")
    if task:
        return str(task)
    return "report"


def run_agentic_flow(
    *,
    session_id: int,
    run_id: int,
    user_message: str,
    is_resume: bool = False,
    # 👇 新增：为了在 adapter 内落库（你要求的）
    db=None,
    user_id: Optional[int] = None,
    save_report: bool = True,
    return_state: bool = False,  # 调试用
) -> Dict[str, Any]:
    config = {"configurable": {"thread_id": f"{session_id}:{run_id}"}}

    if is_resume:
        out_state = app.invoke(Command(resume=user_message), config=config)
    else:
        out_state = app.invoke({"messages": [HumanMessage(content=user_message)]}, config=config)

    # 1) interrupt：直接返回追问
    question = _extract_interrupt_text(out_state)
    if question:
        resp = {"assistant_message": question, "interrupted": True}
        if return_state:
            resp["state"] = out_state
        return resp

    # 2) 不中断：正常返回最后一句 AI（不做“是不是最终报告”的判断）
    last_ai = _extract_last_ai_message(out_state.get("messages"))
    resp: Dict[str, Any] = {
        "assistant_message": last_ai or "（未取到 AI 回复）",
        "interrupted": False,
    }

    # 3) ✅ 仅用于“存库”：如果图里产出了 final_report，就存入数据库
    report_text = out_state.get("final_report")
    if save_report and report_text and db is not None and user_id is not None:
        key = (session_id, run_id)
        if key not in _SAVED:
            # 避免 import 循环：这里再导 crud
            from backend.db import crud

            title = _guess_report_title(out_state)
            r = crud.create_report(
                db,
                user_id=user_id,
                session_id=session_id,
                title=title,
                content=report_text,
            )
            _SAVED.add(key)

            # 给前端展示用：你前端可以优先用 report_content
            resp["report_id"] = getattr(r, "id", None)
            resp["report_content"] = report_text

    if return_state:
        resp["state"] = out_state
    return resp
