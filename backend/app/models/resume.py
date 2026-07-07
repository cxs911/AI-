"""简历模型 - 岗位专属简历生成与存档"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class GeneratedResume(Base):
    """生成的岗位专属简历"""
    __tablename__ = "generated_resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True)
    jd_title = Column(String(200), comment="关联JD标题")
    jd_company = Column(String(200), comment="关联公司")

    # 简历内容
    name = Column(String(50), default="个人信息", comment="姓名")
    personal_info = Column(JSON, comment="个人信息(电话/邮箱/地址等)")
    summary = Column(Text, comment="个人总结/求职意向")
    education = Column(JSON, comment="教育背景")
    work_experience = Column(JSON, comment="工作/项目经历(按模块排序)")
    skills = Column(JSON, comment="技能标签")
    custom_sections = Column(JSON, comment="自定义模块")

    # 模块顺序配置
    section_order = Column(JSON, comment="模块显示顺序")

    # 模板和样式
    template_style = Column(String(50), default="professional", comment="模板风格")
    ats_version = Column(Integer, default=1, comment="ATS优化版本")
    match_score = Column(Integer, comment="匹配度得分0-100")

    # 招呼语
    greeting = Column(Text, comment="一对一招呼语")

    status = Column(String(20), default="draft", comment="状态: draft/completed")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
