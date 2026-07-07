"""JD解析 API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.jd import JobDescription
from app.services.jd_service import jd_service
from app.schemas.jd import JobDescriptionCreate, JobDescriptionResponse, JDParsedResponse
from app.schemas.common import ResponseBase, PaginatedResponse

router = APIRouter(prefix="/api/jd", tags=["JD管理"])


@router.post("", response_model=ResponseBase)
def create_jd(jd: JobDescriptionCreate, db: Session = Depends(get_db)):
    """创建JD"""
    jd_obj = jd_service.create_jd(
        title=jd.title,
        raw_content=jd.raw_content,
        company=jd.company,
        city=jd.city,
        salary_min=jd.salary_min,
        salary_max=jd.salary_max,
        experience=jd.experience,
        education=jd.education,
        source=jd.source,
        source_url=jd.source_url,
        db=db,
    )
    return ResponseBase(data={"id": jd_obj.id, "title": jd_obj.title})


@router.post("/{jd_id}/analyze", response_model=ResponseBase)
async def analyze_jd(jd_id: int, db: Session = Depends(get_db)):
    """AI解析JD - 能力拆解与权重打分"""
    try:
        parsed = await jd_service.analyze_jd(jd_id, db)
        return ResponseBase(data=JDParsedResponse.model_validate(parsed).model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD解析失败: {str(e)}")


@router.get("/list", response_model=PaginatedResponse)
def list_jds(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """JD列表"""
    items, total = jd_service.list_jds(page, page_size, db)
    return PaginatedResponse(
        data=[JobDescriptionResponse.model_validate(m) for m in items],
        pagination={"page": page, "page_size": page_size, "total": total},
    )


@router.get("/{jd_id}", response_model=ResponseBase)
def get_jd(jd_id: int, db: Session = Depends(get_db)):
    """JD详情（含解析结果）"""
    jd = jd_service.get_jd(jd_id, db)
    if not jd:
        raise HTTPException(status_code=404, detail="JD不存在")
    return ResponseBase(data=JobDescriptionResponse.model_validate(jd).model_dump())


@router.delete("/{jd_id}", response_model=ResponseBase)
def delete_jd(jd_id: int, db: Session = Depends(get_db)):
    """删除JD"""
    if jd_service.delete_jd(jd_id, db):
        return ResponseBase(message="删除成功")
    raise HTTPException(status_code=404, detail="JD不存在")


@router.get("/{jd_id}/keywords", response_model=ResponseBase)
def get_keywords(jd_id: int, db: Session = Depends(get_db)):
    """获取JD关键词"""
    keywords = jd_service.get_keywords(jd_id, db)
    return ResponseBase(data=[{"keyword": k.keyword, "weight": k.weight} for k in keywords])


@router.post("/{jd_id}/gap-report", response_model=ResponseBase)
async def generate_gap_report(
    jd_id: int,
    skills: str = Query("[]"),
    db: Session = Depends(get_db),
):
    """生成能力缺口报告"""
    try:
        import json
        user_skills = json.loads(skills)
        report = await jd_service.generate_gap_report(jd_id, user_skills, db)
        return ResponseBase(data={"report": report})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
