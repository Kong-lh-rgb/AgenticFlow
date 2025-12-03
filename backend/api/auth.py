from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_user
from backend.db import crud
from backend.core.security import hash_password, verify_password, create_access_token
from backend.schemas.auth import RegisterReq, TokenResp
from sqlalchemy.exc import IntegrityError
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(data: RegisterReq, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="username already exists")

    try:
        user = crud.create_user(db, data.username, hash_password(data.password))
        return {"user_id": user.id, "username": user.username}

    except IntegrityError as e:
        db.rollback()
        # 常见：唯一键冲突、NOT NULL、外键等
        raise HTTPException(status_code=400, detail=f"DB IntegrityError: {getattr(e, 'orig', e)}")

    except Exception as e:
        db.rollback()
        # 先把真实原因返回出来（开发阶段这样做没问题）
        raise HTTPException(status_code=500, detail=f"DB Error: {e.__class__.__name__}: {e}")

# 注意：这里用表单方式登录，Swagger 的 Authorize 会更丝滑
@router.post("/login", response_model=TokenResp)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form.username)
    if (not user) or (not verify_password(form.password, user.password_hash)):
        raise HTTPException(status_code=401, detail="invalid username or password")
    token = create_access_token(user.id)
    return TokenResp(access_token=token)

@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {"user_id": current_user.id, "username": current_user.username}
