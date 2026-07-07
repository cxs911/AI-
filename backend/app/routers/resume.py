"""简历生成 API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.resume_service import resume_service
from app.services.export_service import export_service
from app.schemas.resume import (
    ResumeGenerateRequest, ResumeGreetingRequest, ResumeResponse,
)
from app.schemas.common import ResponseBase, PaginatedResponse

router = APIRouter(prefix="/api/resumes", tags=["简历生成"])


@router.post("/generate", response_model=ResponseBase)
async def generate_resume(
    req: ResumeGenerateRequest,
    db: Session = Depends(get_db),
):
    """根据JD生成定制简历"""
    try:
        resume = await resume_service.generate_resume(
            jd_id=req.jd_id,
            template_style=req.template_style,
            section_order=req.section_order,
            db=db,
        )
        return ResponseBase(data={
            "id": resume.id,
            "match_score": resume.match_score,
            "summary": resume.summary,
            "skills": resume.skills,
            "work_experience": resume.work_experience,
            "section_order": resume.section_order,
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"简历生成失败: {str(e)}")


@router.post("/{resume_id}/greeting", response_model=ResponseBase)
async def generate_greeting(
    resume_id: int,
    req: ResumeGreetingRequest,
    db: Session = Depends(get_db),
):
    """生成招呼语"""
    try:
        greeting = await resume_service.generate_greeting(
            resume_id, req.style, db
        )
        return ResponseBase(data={"greeting": greeting})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=PaginatedResponse)
def list_resumes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """简历列表"""
    items, total = resume_service.list_resumes(page, page_size, db)
    return PaginatedResponse(
        data=[ResumeResponse.model_validate(m) for m in items],
        pagination={"page": page, "page_size": page_size, "total": total},
    )


@router.get("/{resume_id}", response_model=ResponseBase)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """获取简历详情"""
    resume = resume_service.get_resume(resume_id, db)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    return ResponseBase(data=ResumeResponse.model_validate(resume).model_dump())


@router.delete("/{resume_id}", response_model=ResponseBase)
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    """删除简历"""
    if resume_service.delete_resume(resume_id, db):
        return ResponseBase(message="删除成功")
    raise HTTPException(status_code=404, detail="简历不存在")


@router.post("/{resume_id}/export/pdf", response_model=ResponseBase)
def export_pdf(resume_id: int, db: Session = Depends(get_db)):
    """导出ATS标准PDF"""
    try:
        path = export_service.export_pdf(resume_id, db)
        return ResponseBase(data={"path": path, "url": f"/api/files/{path.split('/')[-1]}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF导出失败: {str(e)}")


@router.get("/{resume_id}/preview", response_model=ResponseBase)
def preview_resume(resume_id: int, db: Session = Depends(get_db)):
    """实时预览简历HTML"""
    try:
        html = export_service._resume_to_html(
            resume_service.get_resume(resume_id, db)
        )
        return ResponseBase(data={"html": html})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
