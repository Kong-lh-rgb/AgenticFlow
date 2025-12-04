from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_user
from backend.db import crud

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/mine")
def my_reports(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rows = crud.list_reports_by_user(db, current_user.id)
    return [{"id": r.id, "title": r.title, "created_at": r.created_at, "session_id": r.session_id} for r in rows]

@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    r = crud.get_report_by_id(db, report_id)
    if not r or r.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="report not found")
    return {
        "id": r.id,
        "session_id": r.session_id,
        "title": r.title,
        "content": r.content,
        "created_at": r.created_at,
    }