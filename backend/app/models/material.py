"""个人素材库模型 - 简历原始素材、标签管理"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# 素材-标签 多对多关联表
material_tag_table = Table(
    "material_tag_link",
    Base.metadata,
    Column("material_id", Integer, ForeignKey("materials.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Material(Base):
    """个人素材 - 原始简历/文档素材"""
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="素材标题")
    file_type = Column(String(20), nullable=False, comment="文件类型: pdf/word/txt")
    file_path = Column(String(500), comment="文件存储路径")
    raw_text = Column(Text, comment="解析后的原始文本")
    structured_data = Column(Text, comment="结构化数据(JSON)")
    category = Column(String(50), default="general", comment="分类")
    source = Column(String(50), default="upload", comment="来源: upload/import")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    tags = relationship("Tag", secondary=material_tag_table, back_populates="materials")


class Tag(Base):
    """标签分类"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="标签名称")
    color = Column(String(7), default="#409EFF", comment="标签颜色")
    created_at = Column(DateTime, default=datetime.now)

    materials = relationship("Material", secondary=material_tag_table, back_populates="tags")


class Experience(Base):
    """经历库 - 课程/校园/工作经历"""
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="经历标题")
    category = Column(String(50), nullable=False, comment="类型: course/school/work/project")
    start_date = Column(String(20), comment="开始时间")
    end_date = Column(String(20), comment="结束时间")
    role = Column(String(100), comment="角色/职位")
    organization = Column(String(200), comment="组织/公司/学校")
    original_desc = Column(Text, comment="原始描述")
    star_desc = Column(Text, comment="STAR量化描述")
    skills = Column(Text, comment="涉及技能(JSON数组)")
    achievements = Column(Text, comment="成果数据(JSON)")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
