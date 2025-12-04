from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import User, Session as ChatSession, Message, Report

def get_user_by_username(db: Session, username: str):
    return db.scalar(select(User).where(User.username == username))

def get_user_by_id(db: Session, user_id: int):
    return db.get(User, user_id)

def create_user(db: Session, username: str, password_hash: str):
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_session(db: Session, user_id: int, title: str | None = None):
    s = ChatSession(user_id=user_id, title=title, status="active")
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def add_message(db: Session, session_id: int, role: str, run_id: int,content: str):
    m = Message(session_id=session_id, role=role,  run_id=run_id, content=content)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def list_messages(db: Session, session_id: int,run_id: int, limit: int = 50):
    stmt = select(Message).where(Message.session_id == session_id, Message.run_id == run_id).order_by(Message.id.desc()).limit(limit)
    rows = db.scalars(stmt).all()
    return list(reversed(rows))

def create_report(db: Session, user_id: int, session_id: int, title: str | None, content: str):
    r = Report(user_id=user_id, session_id=session_id, title=title, content=content)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def list_reports_by_user(db: Session, user_id: int, limit: int = 50):
    stmt = select(Report).where(Report.user_id == user_id).order_by(Report.id.desc()).limit(limit)
    return db.scalars(stmt).all()

def get_report(db: Session, report_id: int):
    return db.get(Report, report_id)

from sqlalchemy import select
from backend.db.models import Session as ChatSession

def get_session_by_id(db, session_id: int):
    return db.scalar(select(ChatSession).where(ChatSession.id == session_id))

def bump_run(db: Session, session_obj):
    session_obj.active_run_id += 1
    session_obj.status = "active"
    db.commit()
    db.refresh(session_obj)
    return session_obj.active_run_id

