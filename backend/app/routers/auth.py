"""用户认证 API路由 - 登录/注册/注销/改密"""
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User, UserToken
from app.schemas.auth import (
    LoginRequest, RegisterRequest, ChangePasswordRequest, UserResponse,
)
from app.schemas.common import ResponseBase

router = APIRouter(prefix="/api/auth", tags=["用户认证"])
logger = logging.getLogger(__name__)

TOKEN_EXPIRE_DAYS = 30


def get_current_user(token: str = Header(None, alias="Authorization"), db: Session = Depends(get_db)) -> User:
    """从请求头提取当前用户（依赖注入）"""
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    if token.startswith("Bearer "):
        token = token[7:]
    token_record = db.query(UserToken).filter(
        UserToken.token == token,
    ).first()
    if not token_record:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user


@router.post("/login", response_model=ResponseBase)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not user.verify_password(req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    # 生成 token
    import secrets
    token_str = secrets.token_urlsafe(48)
    token = UserToken(
        user_id=user.id,
        token=token_str,
        expires_at=datetime.now() + timedelta(days=TOKEN_EXPIRE_DAYS),
    )
    db.add(token)
    db.commit()

    return ResponseBase(data={
        "token": token_str,
        "user": {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
        }
    })


@router.post("/register", response_model=ResponseBase)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """注册新用户"""
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    if len(req.username) < 2 or len(req.password) < 6:
        raise HTTPException(status_code=400, detail="用户名至少2位，密码至少6位")

    user = User(
        username=req.username,
        password_hash=User.hash_password(req.password),
        display_name=req.display_name or req.username,
    )
    db.add(user)
    db.commit()

    return ResponseBase(message="注册成功，请登录", data={"username": req.username})


@router.post("/logout", response_model=ResponseBase)
def logout(
    token: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    """退出登录（清除当前 Token）"""
    if token:
        if token.startswith("Bearer "):
            token = token[7:]
        db.query(UserToken).filter(UserToken.token == token).delete()
        db.commit()
    return ResponseBase(message="已退出登录")


@router.get("/me", response_model=ResponseBase)
def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return ResponseBase(data=UserResponse.model_validate(user).model_dump())


@router.post("/change-password", response_model=ResponseBase)
def change_password(
    req: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码"""
    if not user.verify_password(req.old_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少6位")
    user.password_hash = User.hash_password(req.new_password)
    db.commit()
    # 清除所有旧 token，强制重新登录
    db.query(UserToken).filter(UserToken.user_id == user.id).delete()
    db.commit()
    return ResponseBase(message="密码已修改，请重新登录")
