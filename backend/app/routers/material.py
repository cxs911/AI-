"""个人素材库 API路由"""
import os
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.material import Material, Tag, Experience
from app.services.material_service import material_service
from app.schemas.material import (
    MaterialCreate, MaterialResponse, MaterialUpdate,
    TagCreate, TagResponse,
    ExperienceCreate, ExperienceResponse, ExperienceUpdate,
)
from app.schemas.common import ResponseBase, PaginatedResponse
from app.config import settings

router = APIRouter(prefix="/api/materials", tags=["素材库"])
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=ResponseBase)
async def upload_material(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("general"),
    tags: str = Form("[]"),
    db: Session = Depends(get_db),
):
    """上传并解析简历文件"""
    try:
        # 保存上传文件
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        tag_list = []
        try:
            import json
            tag_list = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            if tags and tags != "[]":
                tag_list = [tags]

        material = await material_service.upload_and_parse(
            file_path, title, category, tag_list, db
        )
        return ResponseBase(data={"id": material.id, "title": material.title})
    except Exception as e:
        logger.error(f"上传素材失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=PaginatedResponse)
def list_materials(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """素材列表"""
    items, total = material_service.list_materials(category, tag, page, page_size, db)
    return PaginatedResponse(
        data=[MaterialResponse.model_validate(m) for m in items],
        pagination={"page": page, "page_size": page_size, "total": total},
    )


@router.get("/{material_id}", response_model=ResponseBase)
def get_material(material_id: int, db: Session = Depends(get_db)):
    """获取素材详情"""
    material = material_service.get_material(material_id, db)
    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")
    return ResponseBase(data=MaterialResponse.model_validate(material).model_dump())


@router.delete("/{material_id}", response_model=ResponseBase)
def delete_material(material_id: int, db: Session = Depends(get_db)):
    """删除素材"""
    if material_service.delete_material(material_id, db):
        return ResponseBase(message="删除成功")
    raise HTTPException(status_code=404, detail="素材不存在")


# 标签管理
@router.post("/tags", response_model=ResponseBase)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    t = material_service.create_tag(tag.name, tag.color, db)
    return ResponseBase(data={"id": t.id, "name": t.name})


@router.get("/tags", response_model=ResponseBase)
def list_tags(db: Session = Depends(get_db)):
    """标签列表"""
    tags = material_service.list_tags(db)
    return ResponseBase(data=tags)


# 经历管理
@router.post("/experiences", response_model=ResponseBase)
async def create_experience(exp: ExperienceCreate, db: Session = Depends(get_db)):
    """创建经历"""
    experience = Experience(
        title=exp.title,
        category=exp.category,
        start_date=exp.start_date,
        end_date=exp.end_date,
        role=exp.role,
        organization=exp.organization,
        original_desc=exp.original_desc,
        skills="[]",
    )
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return ResponseBase(data={"id": experience.id})


@router.get("/experiences", response_model=PaginatedResponse)
def list_experiences(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """经历列表"""
    query = db.query(Experience)
    if category:
        query = query.filter(Experience.category == category)
    total = query.count()
    items = query.order_by(Experience.updated_at.desc()).offset(
        (page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[ExperienceResponse.model_validate(m) for m in items],
        pagination={"page": page, "page_size": page_size, "total": total},
    )


@router.post("/experiences/{exp_id}/optimize", response_model=ResponseBase)
async def optimize_experience(
    exp_id: int,
    jd_keywords: str = Form("[]"),
    db: Session = Depends(get_db),
):
    """AI优化经历为STAR描述"""
    try:
        import json
        keywords = json.loads(jd_keywords)
        exp = await material_service.optimize_experience(exp_id, keywords, db)
        return ResponseBase(data={
            "star_desc": exp.star_desc,
            "skills": exp.skills,
            "achievements": exp.achievements,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/experiences/{exp_id}", response_model=ResponseBase)
def delete_experience(exp_id: int, db: Session = Depends(get_db)):
    """删除经历"""
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="经历不存在")
    db.delete(exp)
    db.commit()
    return ResponseBase(message="删除成功")
