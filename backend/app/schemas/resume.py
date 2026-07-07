"""简历生成数据模型"""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class PersonalInfo(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    location: str = ""
    title: str = ""
    website: Optional[str] = None


class Education(BaseModel):
    school: str = ""
    degree: str = ""
    major: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: Optional[str] = None


class WorkExperience(BaseModel):
    company: str = ""
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    achievements: List[str] = []


class ResumeGenerateRequest(BaseModel):
    """生成简历请求"""
    jd_id: int
    template_style: str = "professional"
    section_order: Optional[List[str]] = None


class ResumeGreetingRequest(BaseModel):
    """生成招呼语请求"""
    resume_id: int
    style: str = "fresh"  # fresh/social


class ResumeResponse(BaseModel):
    id: int
    jd_id: Optional[int] = None
    jd_title: Optional[str] = None
    jd_company: Optional[str] = None
    name: str = ""
    personal_info: Optional[dict] = None
    summary: Optional[str] = None
    education: Optional[list] = None
    work_experience: Optional[list] = None
    skills: Optional[list] = None
    custom_sections: Optional[list] = None
    section_order: Optional[list] = None
    template_style: str = "professional"
    match_score: Optional[int] = None
    greeting: Optional[str] = None
    status: str = "draft"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
