"""投递管理 API路由 - Boss岗位检索、投递、统计"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.services.delivery_service import delivery_service
from app.schemas.delivery import (
    DeliveryJobResponse, BossSearchRequest, BatchDeliveryRequest,
    DeliveryStatsResponse,
)
from app.schemas.common import ResponseBase, PaginatedResponse

router = APIRouter(prefix="/api/delivery", tags=["投递管理"])


# ===== 浏览器管理 =====
@router.post("/browser/start", response_model=ResponseBase)
def start_browser():
    """启动Chrome浏览器（可视化）"""
    try:
        delivery_service.start_browser()
        return ResponseBase(message="浏览器已启动，请在打开的窗口扫码登录Boss直聘")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"浏览器启动失败: {str(e)}")


@router.post("/browser/wait-login", response_model=ResponseBase)
def wait_login(timeout: int = Query(120, ge=30)):
    """等待扫码登录"""
    success = delivery_service.wait_login(timeout)
    if success:
        return ResponseBase(message="登录成功")
    return ResponseBase(code=408, message="登录超时，请重新扫码")


@router.post("/browser/close", response_model=ResponseBase)
def close_browser():
    """关闭浏览器"""
    delivery_service.close_browser()
    return ResponseBase(message="浏览器已关闭")


@router.get("/browser/status", response_model=ResponseBase)
def browser_status():
    """获取浏览器状态"""
    client = delivery_service.get_boss_client()
    return ResponseBase(data={
        "running": client.driver is not None,
        "paused": client.is_paused,
        "today_deliveries": client.today_deliveries,
        "delivery_limit": 25,
    })


# ===== 岗位搜索 =====
@router.post("/search", response_model=ResponseBase)
async def search_jobs(req: BossSearchRequest, db: Session = Depends(get_db)):
    """搜索Boss岗位"""
    try:
        client = delivery_service.get_boss_client()
        if not client.driver:
            raise HTTPException(status_code=400, detail="浏览器未启动")

        jobs = client.search_jobs(
            keyword=req.keywords,
            city=req.city,
            page=req.page,
            salary_min=req.salary_min,
            salary_max=req.salary_max,
        )

        # 保存到数据库
        saved = delivery_service.save_jobs(jobs, db)

        # 如果有匹配度算法，计算匹配度
        from app.models.resume import GeneratedResume
        latest_resume = db.query(GeneratedResume).order_by(
            GeneratedResume.created_at.desc()
        ).first()

        if latest_resume and saved:
            for job in saved[:5]:  # 前5个计算匹配度
                try:
                    from app.utils.llm_client import get_llm_client
                    match = await get_llm_client().calculate_match_score(
                        {"skills": latest_resume.skills or [],
                         "summary": latest_resume.summary or ""},
                        {"title": job.title, "company": job.company,
                         "tags": job.tags or []}
                    )
                    job.match_score = match.get("total_score", 0)
                except Exception:
                    pass
            db.commit()

        return ResponseBase(data={
            "total": len(jobs),
            "saved": len(saved),
            "jobs": jobs,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 投递列表 =====
@router.get("/jobs", response_model=PaginatedResponse)
def list_delivery_jobs(
    status: Optional[str] = None,
    is_filtered: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """投递岗位列表"""
    items, total = delivery_service.list_delivery_jobs(
        status, is_filtered, page, page_size, db
    )
    return PaginatedResponse(
        data=[DeliveryJobResponse.model_validate(m) for m in items],
        pagination={"page": page, "page_size": page_size, "total": total},
    )


@router.post("/jobs/{job_id}/deliver", response_model=ResponseBase)
async def deliver_single(job_id: int, db: Session = Depends(get_db)):
    """手动投递单个岗位"""
    try:
        from app.models.delivery import DeliveryJob
        # 获取招呼语
        job = db.query(DeliveryJob).filter(DeliveryJob.id == job_id).first()
        greeting = job.greeting if job else ""

        success = await delivery_service.deliver_single(job_id, greeting, db)
        if success:
            return ResponseBase(message="投递成功")
        return ResponseBase(code=500, message="投递失败，请查看日志")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-deliver", response_model=ResponseBase)
async def deliver_batch(req: BatchDeliveryRequest, db: Session = Depends(get_db)):
    """批量投递（需开启人工审核开关）"""
    try:
        if not req.enable_review:
            return ResponseBase(code=400, message="请先开启【人工审核开关】")
        results = await delivery_service.deliver_batch(
            req.job_ids, req.enable_review, db
        )
        return ResponseBase(data=results, message=f"投递完成: 成功{results['success']}个")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 统计 =====
@router.get("/stats", response_model=ResponseBase)
def get_stats(days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    """投递统计看板"""
    stats = delivery_service.get_stats(days, db)
    return ResponseBase(data=[DeliveryStatsResponse.model_validate(s) for s in stats])


# ===== 风控配置 =====
@router.get("/risk-config", response_model=ResponseBase)
def get_risk_config(db: Session = Depends(get_db)):
    """获取风控配置"""
    from app.models.delivery import RiskControl
    configs = db.query(RiskControl).all()
    return ResponseBase(data=[
        {"key": c.key, "value": c.value, "description": c.description}
        for c in configs
    ])


@router.post("/risk-config", response_model=ResponseBase)
def update_risk_config(
    key: str = Body(...),
    value: str = Body(...),
    description: str = Body(""),
    db: Session = Depends(get_db),
):
    """更新风控配置"""
    delivery_service.update_risk_config(key, value, description, db)
    return ResponseBase(message="配置已更新")
