"""JD解析数据模型"""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class JobDescriptionCreate(BaseModel):
    title: str
    company: Optional[str] = None
    city: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    raw_content: str
    source: str = "manual"
    source_url: Optional[str] = None


class JobDescriptionUpdate(BaseModel):
    title: Optional[str] = None
    raw_content: Optional[str] = None


class SkillRequirement(BaseModel):
    name: str
    weight: int = 50
    level: str = "了解"
    have_gap: bool = False
    gap_description: Optional[str] = None


class JDParsedResponse(BaseModel):
    id: int
    jd_id: int
    core_skills: Optional[List[SkillRequirement]] = None
    soft_skills: Optional[List[dict]] = None
    responsibilities: Optional[List[dict]] = None
    keywords: Optional[List[str]] = None
    total_score: Optional[float] = None
    gap_report: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    city: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    raw_content: Optional[str] = None
    source: str = "manual"
    source_url: Optional[str] = None
    is_active: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    parsed_result: Optional[JDParsedResponse] = None

    class Config:
        from_attributes = True
