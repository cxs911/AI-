"""个人素材库数据模型"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TagBase(BaseModel):
    name: str
    color: str = "#409EFF"


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    created_at: Optional[datetime] = None
    material_count: int = 0

    class Config:
        from_attributes = True


class MaterialBase(BaseModel):
    title: str
    category: str = "general"
    tags: List[str] = []


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class MaterialResponse(MaterialBase):
    id: int
    file_type: str = ""
    file_path: Optional[str] = None
    raw_text: Optional[str] = None
    structured_data: Optional[str] = None
    source: str = "upload"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


class ExperienceBase(BaseModel):
    title: str
    category: str = "work"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    role: Optional[str] = None
    organization: Optional[str] = None
    original_desc: Optional[str] = None
    star_desc: Optional[str] = None
    skills: Optional[List[str]] = None
    achievements: Optional[dict] = None


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    star_desc: Optional[str] = None
    skills: Optional[List[str]] = None
    achievements: Optional[dict] = None


class ExperienceResponse(ExperienceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
