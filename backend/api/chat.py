from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_user
from backend.db import crud
from backend.schemas.chat import ChatSendReq
from backend.graph_adapter import run_agentic_flow

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/send")
def send_message(data: ChatSendReq, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    s = crud.get_session_by_id(db, data.session_id)
    if not s or s.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="session not found")

    # 1) 先存用户消息
    crud.add_message(db, data.session_id, "user", data.content)

    # 2) 跑图（这里不再传 history dict！图内 messages 是 BaseMessage）
    out = run_agentic_flow(session_id=data.session_id, user_message=data.content)

    assistant = out["assistant_message"]
    crud.add_message(db, data.session_id, "assistant", assistant)

    report_id = None
    report = out.get("report")
    if report and report.get("content"):
        r = crud.create_report(
            db,
            user_id=current_user.id,
            session_id=data.session_id,
            title=report.get("title"),
            content=report["content"],
        )
        report_id = r.id

    return {"assistant_message": assistant, "report_id": report_id, "interrupted": out.get("interrupted", False)}

@router.get("/history")
def history(
    session_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = crud.get_session_by_id(db, session_id)
    if not s or s.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="session not found")

    msgs = crud.list_messages(db, session_id=session_id, limit=limit)
    return [
        {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at}
        for m in msgs
    ]