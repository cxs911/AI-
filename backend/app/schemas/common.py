"""通用数据模型"""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ResponseBase(BaseModel):
    """统一响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


class Pagination(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 20
    total: int = 0


class PaginatedResponse(ResponseBase):
    """分页响应"""
    data: Optional[list] = None
    pagination: Optional[Pagination] = None
