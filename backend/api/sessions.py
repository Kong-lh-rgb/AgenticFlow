from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_user
from backend.db import crud
from backend.schemas.session import SessionCreateReq

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/create")
def create_session(data: SessionCreateReq, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    s = crud.create_session(db, user_id=current_user.id, title=data.title)
    return {"session_id": s.id, "title": s.title, "status": s.status}
