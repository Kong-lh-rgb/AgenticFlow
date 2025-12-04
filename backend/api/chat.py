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

    # 1) 如果当前处于 waiting，必须 resume，不能开新 run
    if s.status == "waiting":
        run_id = s.active_run_id
        is_resume = True
    else:
        # 2) 不在 waiting：可以选择开新 run
        if data.new_run:
            run_id = crud.bump_run(db, s)   # active_run_id += 1
        else:
            run_id = s.active_run_id
        is_resume = False

    # 3) 记录用户消息（带 run_id）
    crud.add_message(db, data.session_id, "user", run_id, data.content)


    # 4) 跑图（thread_id = session_id:run_id）
    out = run_agentic_flow(
        session_id=data.session_id,
        run_id=run_id,
        user_message=data.content,
        is_resume=is_resume,
        db=db,
        user_id=current_user.id,
        save_report=True,
    )

    # 5) 如果 interrupt：把 session 标记 waiting
    if out.get("interrupted"):
        s.status = "waiting"
        db.commit()
        return {"assistant_message": out["assistant_message"], "run_id": run_id, "report_id": None}

    # 6) 正常：恢复 active
    s.status = "active"
    db.commit()

    assistant = out.get("assistant_message") or ""
    crud.add_message(db, data.session_id, "assistant", run_id, assistant)


    report_obj = out.get("report")
    report_id = None
    report_content = None
    report_title = None
    if isinstance(report_obj, dict) and report_obj.get("content"):
        r = crud.create_report(db,
            user_id=current_user.id,
            session_id=data.session_id,
            title=report_obj.get("title"),
            content=report_obj["content"],
        )
        report_id = r.id
        report_content = r.content
        report_title = r.title

    return {
      "assistant_message": assistant,
      "run_id": run_id,
      "report_id": report_id,
      "report_content": report_content,
      "report_title": report_title,
    }



@router.get("/history")
def history(session_id: int, run_id: int | None = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    s = crud.get_session_by_id(db, session_id)
    if not s or s.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="session not found")

    run_id = run_id or s.active_run_id
    msgs = crud.list_messages(db, session_id, run_id, limit=200)
    return [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at} for m in msgs]
