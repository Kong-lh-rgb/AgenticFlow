from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now(), nullable=False)

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    active_run_id = mapped_column(BigInteger, nullable=False, server_default="1")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sessions.id"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user/assistant/system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    run_id = mapped_column(BigInteger, nullable=False, server_default="1", index=True)

    created_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    session = relationship("Session")

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sessions.id"), index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    run_id = mapped_column(BigInteger, nullable=False, server_default="1", index=True)

    created_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User")
    session = relationship("Session")
