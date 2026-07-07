"""JD解析模型 - 岗位描述、能力拆解、匹配度"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class JobDescription(Base):
    """JD主表 - 从Boss抓取或手动输入的岗位描述"""
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="岗位名称")
    company = Column(String(200), comment="公司名称")
    city = Column(String(50), comment="城市")
    salary_min = Column(Integer, comment="薪资下限(K)")
    salary_max = Column(Integer, comment="薪资上限(K)")
    experience = Column(String(50), comment="经验要求")
    education = Column(String(50), comment="学历要求")
    raw_content = Column(Text, comment="原始JD文本")
    source = Column(String(20), default="manual", comment="来源: boss/manual")
    source_url = Column(String(500), comment="Boss直聘URL")
    is_active = Column(Integer, default=1, comment="是否有效")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 解析结果
    parsed_result = relationship("JDParsed", uselist=False, back_populates="jd", cascade="all,delete")


class JDParsed(Base):
    """JD解析结果 - 能力拆解、权重打分"""
    __tablename__ = "jd_parsed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"), unique=True)

    # 核心能力要求 (JSON)
    core_skills = Column(JSON, comment="核心能力及权重: [{\"name\":\"Python\",\"weight\":90,\"level\":\"熟练\"}]")
    # 软性要求
    soft_skills = Column(JSON, comment="软性能力要求")
    # 岗位职责解析
    responsibilities = Column(JSON, comment="岗位职责拆解")
    # 关键词集合
    keywords = Column(JSON, comment="JD关键词列表")
    # 综合评分
    total_score = Column(Float, comment="综合能力要求评分")
    # 个人能力缺口
    gap_report = Column(Text, comment="能力缺口报告")

    created_at = Column(DateTime, default=datetime.now)

    jd = relationship("JobDescription", back_populates="parsed_result")


class JDKeyword(Base):
    """JD关键词库 - 用于简历包装"""
    __tablename__ = "jd_keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"))
    keyword = Column(String(100), nullable=False, comment="关键词")
    category = Column(String(50), comment="分类: tech/business/soft")
    weight = Column(Integer, default=50, comment="权重1-100")
    count = Column(Integer, default=1, comment="出现次数")

    created_at = Column(DateTime, default=datetime.now)
