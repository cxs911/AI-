"""JD解析服务 - 智能解析、能力拆解、缺口分析"""
import json
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.jd import JobDescription, JDParsed, JDKeyword
from app.utils.llm_client import get_llm_client
from app.config import settings

logger = logging.getLogger(__name__)


class JDService:

    def create_jd(self, title: str, raw_content: str, company: str = None,
                  city: str = None, salary_min: int = None, salary_max: int = None,
                  experience: str = None, education: str = None,
                  source: str = "manual", source_url: str = None,
                  db: Session = None) -> JobDescription:
        """创建JD"""
        jd = JobDescription(
            title=title,
            company=company,
            city=city,
            salary_min=salary_min,
            salary_max=salary_max,
            experience=experience,
            education=education,
            raw_content=raw_content,
            source=source,
            source_url=source_url,
        )
        db.add(jd)
        db.commit()
        db.refresh(jd)
        return jd

    async def analyze_jd(self, jd_id: int, db: Session = None) -> JDParsed:
        """解析JD - 调用Ollama进行能力拆解"""
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not jd:
            raise ValueError("JD不存在")

        if not jd.raw_content:
            raise ValueError("JD内容为空")

        # 调用LLM分析
        result = await get_llm_client().analyze_jd(jd.raw_content)

        # 保存解析结果
        parsed = JDParsed(
            jd_id=jd_id,
            core_skills=result.get("core_skills", []),
            soft_skills=result.get("soft_skills", []),
            responsibilities=result.get("responsibilities", []),
            keywords=result.get("keywords", []),
            total_score=result.get("total_score", 0),
        )
        db.add(parsed)

        # 保存关键词
        keywords = result.get("keywords", [])
        for i, kw in enumerate(keywords):
            if isinstance(kw, str):
                keyword = JDKeyword(
                    jd_id=jd_id,
                    keyword=kw,
                    category="tech",
                    weight=50,
                )
                db.add(keyword)

        db.commit()
        db.refresh(parsed)
        return parsed

    def get_jd(self, jd_id: int, db: Session = None) -> Optional[JobDescription]:
        return db.query(JobDescription).filter(
            JobDescription.id == jd_id
        ).first()

    def list_jds(self, page: int = 1, page_size: int = 20,
                 db: Session = None):
        query = db.query(JobDescription).filter(JobDescription.is_active == 1)
        total = query.count()
        items = query.order_by(JobDescription.updated_at.desc()).offset(
            (page - 1) * page_size).limit(page_size).all()
        return items, total

    def delete_jd(self, jd_id: int, db: Session = None) -> bool:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not jd:
            return False
        db.delete(jd)
        db.commit()
        return True

    def get_keywords(self, jd_id: int, db: Session = None):
        return db.query(JDKeyword).filter(JDKeyword.jd_id == jd_id).all()

    async def generate_gap_report(self, jd_id: int,
                                  user_skills: list,
                                  db: Session = None) -> str:
        """生成个人能力缺口报告"""
        jd = self.get_jd(jd_id, db)
        if not jd or not jd.parsed_result:
            raise ValueError("JD未解析")

        core_skills = jd.parsed_result.core_skills or []
        prompt_data = {
            "required_skills": core_skills,
            "my_skills": user_skills,
        }

        # 标记缺口
        for skill in core_skills:
            skill["have_gap"] = skill.get("name", "") not in [s.get("name", "") for s in user_skills]
            skill["gap_description"] = ""

        jd.parsed_result.core_skills = core_skills
        jd.parsed_result.gap_report = json.dumps(prompt_data, ensure_ascii=False)
        db.commit()
        return jd.parsed_result.gap_report


jd_service = JDService()
