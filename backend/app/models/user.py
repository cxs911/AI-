"""用户与认证模型"""
import hashlib
import secrets
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base


class User(Base):
    """用户账号"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(200), nullable=False, comment="密码哈希")
    display_name = Column(String(50), default="用户", comment="显示名称")
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @staticmethod
    def hash_password(password: str) -> str:
        """用 PBKDF2-SHA256 哈希密码"""
        salt = secrets.token_hex(16)
        h = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${h.hex()}"

    def verify_password(self, password: str) -> bool:
        """验证密码"""
        try:
            salt, _ = self.password_hash.split('$', 1)
            h = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return f"{salt}${h.hex()}" == self.password_hash
        except (ValueError, AttributeError):
            return False


class UserToken(Base):
    """用户登录令牌"""
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(100), unique=True, nullable=False, comment="登录令牌")
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=True, comment="过期时间")
