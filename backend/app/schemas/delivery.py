"""投递管理数据模型"""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class DeliveryJobResponse(BaseModel):
    id: int
    job_id: str
    title: str
    company: Optional[str] = None
    city: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_str: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    tags: Optional[list] = None
    url: Optional[str] = None
    match_score: Optional[int] = None
    is_filtered: int = 0
    filter_reason: Optional[str] = None
    greeting: Optional[str] = None
    delivery_status: str = "pending"
    delivered_at: Optional[datetime] = None
    need_manual_review: int = 1
    boss_info: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeliveryStatsResponse(BaseModel):
    date: str
    total_deliveries: int = 0
    reads: int = 0
    replies: int = 0
    interviews: int = 0
    captcha_triggers: int = 0

    class Config:
        from_attributes = True


class BatchDeliveryRequest(BaseModel):
    """批量投递请求"""
    job_ids: List[int]
    enable_review: bool = False  # 人工审核开关


class BossSearchRequest(BaseModel):
    """Boss岗位搜索请求"""
    keywords: str = ""
    city: str = "北京"
    page: int = 1
    salary_min: int = 0
    salary_max: int = 100
    auto_scrape: bool = False


class BossJobItem(BaseModel):
    """Boss岗位项"""
    job_id: str
    title: str
    company: str
    city: str
    salary: str
    salary_min: int = 0
    salary_max: int = 0
    experience: str = ""
    education: str = ""
    tags: List[str] = []
    url: str = ""
    boss_name: str = ""
    boss_title: str = ""
    match_score: int = 0
