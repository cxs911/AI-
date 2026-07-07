"""投递管理模型 - 投递记录、统计、风控"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class DeliveryJob(Base):
    """投递任务 - 从Boss抓取的匹配岗位"""
    __tablename__ = "delivery_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(100), unique=True, comment="Boss岗位ID")
    title = Column(String(200), nullable=False, comment="岗位名称")
    company = Column(String(200), comment="公司名称")
    city = Column(String(50), comment="城市")
    salary_min = Column(Integer, comment="薪资下限(K)")
    salary_max = Column(Integer, comment="薪资上限(K)")
    salary_str = Column(String(100), comment="薪资字符串")
    experience = Column(String(50), comment="经验要求")
    education = Column(String(50), comment="学历要求")
    tags = Column(JSON, comment="岗位标签")
    url = Column(String(500), comment="岗位URL")
    match_score = Column(Integer, comment="匹配度0-100")
    is_filtered = Column(Integer, default=0, comment="是否被过滤(外包/培训)")
    filter_reason = Column(String(200), comment="过滤原因")

    # 关联简历/话术
    resume_id = Column(Integer, ForeignKey("generated_resumes.id", ondelete="SET NULL"), nullable=True)
    greeting = Column(Text, comment="生成的招呼语")

    # 投递状态
    delivery_status = Column(String(20), default="pending",
                             comment="pending/ready/delivered/replied/interviewed/failed")
    delivered_at = Column(DateTime, comment="投递时间")
    need_manual_review = Column(Integer, default=1, comment="是否需要人工审核")

    # Boss数据
    boss_info = Column(JSON, comment="Boss信息(name,title等)")
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    resume = relationship("GeneratedResume")


class DeliveryRecord(Base):
    """投递记录 - 详细的投递日志"""
    __tablename__ = "delivery_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_job_id = Column(Integer, ForeignKey("delivery_jobs.id", ondelete="CASCADE"))
    action = Column(String(50), nullable=False, comment="动作: deliver/read/reply/interview/captcha")
    detail = Column(Text, comment="详情")
    created_at = Column(DateTime, default=datetime.now)


class DeliveryStats(Base):
    """投递统计"""
    __tablename__ = "delivery_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(20), nullable=False, comment="日期 YYYY-MM-DD")
    total_deliveries = Column(Integer, default=0, comment="当日投递数")
    reads = Column(Integer, default=0, comment="已读数")
    replies = Column(Integer, default=0, comment="回复数")
    interviews = Column(Integer, default=0, comment="面试邀请数")
    captcha_triggers = Column(Integer, default=0, comment="触发验证次数")
    is_active = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.now)


class RiskControl(Base):
    """风控配置"""
    __tablename__ = "risk_control"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, comment="配置项")
    value = Column(Text, comment="配置值")
    description = Column(String(200), comment="描述")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
