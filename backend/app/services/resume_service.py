"""简历生成服务 - AI定制简历、招呼语生成"""
import json
import logging
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from app.models.resume import GeneratedResume
from app.models.material import Experience
from app.models.jd import JobDescription
from app.utils.llm_client import get_llm_client
from app.config import settings

logger = logging.getLogger(__name__)


class ResumeService:

    async def generate_resume(self, jd_id: int,
                              template_style: str = "professional",
                              section_order: List[str] = None,
                              user_info: dict = None,
                              db: Session = None) -> GeneratedResume:
        """根据JD生成定制简历"""
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not jd:
            raise ValueError("JD不存在")

        # 获取JD分析结果
        jd_analysis = {}
        if jd.parsed_result:
            jd_analysis = {
                "core_skills": jd.parsed_result.core_skills or [],
                "keywords": jd.parsed_result.keywords or [],
                "responsibilities": jd.parsed_result.responsibilities or [],
            }

        # 获取经历库
        experiences = db.query(Experience).all()
        star_experiences = []
        for exp in experiences:
            exp_data = {
                "title": exp.title,
                "category": exp.category,
                "organization": exp.organization,
                "role": exp.role,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "star_desc": exp.star_desc or exp.original_desc,
            }
            star_experiences.append(exp_data)

        # 默认用户信息
        if not user_info:
            user_info = {
                "name": "求职者",
                "phone": "",
                "email": "",
                "education": [],
                "skills": [],
            }

        # 调用LLM生成简历
        client = get_llm_client()
        result = await client.generate_resume(
            user_info, jd_analysis, star_experiences, template_style
        )

        # 计算匹配度
        match_result = await client.calculate_match_score(
            {"skills": result.get("skills", []), "experience_summary": str(star_experiences[:3])},
            jd_analysis
        )
        match_score = match_result.get("total_score", 0)

        # 保存简历
        resume = GeneratedResume(
            jd_id=jd_id,
            jd_title=jd.title,
            jd_company=jd.company,
            summary=result.get("summary", ""),
            work_experience=result.get("work_experience", []),
            skills=result.get("skills", []),
            section_order=section_order or result.get("section_order",
                                                       ["summary", "skills", "experience", "education"]),
            template_style=template_style,
            match_score=match_score,
            status="completed",
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    async def generate_greeting(self, resume_id: int,
                                style: str = "fresh",
                                db: Session = None) -> str:
        """生成一对一招呼语"""
        resume = db.query(GeneratedResume).filter(
            GeneratedResume.id == resume_id
        ).first()
        if not resume:
            raise ValueError("简历不存在")

        resume_info = {
            "name": resume.name,
            "summary": resume.summary,
            "skills": resume.skills or [],
            "experience_count": len(resume.work_experience or []),
        }
        job_info = {
            "title": resume.jd_title or "",
            "company": resume.jd_company or "",
        }

        greeting = await get_llm_client().generate_greeting(resume_info, job_info, style)
        resume.greeting = greeting
        db.commit()
        return greeting

    def get_resume(self, resume_id: int, db: Session = None) -> Optional[GeneratedResume]:
        return db.query(GeneratedResume).filter(GeneratedResume.id == resume_id).first()

    def list_resumes(self, page: int = 1, page_size: int = 20,
                     db: Session = None):
        query = db.query(GeneratedResume)
        total = query.count()
        items = query.order_by(GeneratedResume.updated_at.desc()).offset(
            (page - 1) * page_size).limit(page_size).all()
        return items, total

    def delete_resume(self, resume_id: int, db: Session = None) -> bool:
        resume = db.query(GeneratedResume).filter(GeneratedResume.id == resume_id).first()
        if not resume:
            return False
        db.delete(resume)
        db.commit()
        return True


resume_service = ResumeService()
