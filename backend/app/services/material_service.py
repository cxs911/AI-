"""个人素材库服务 - 简历解析入库、标签管理"""
import os
import json
import shutil
import logging
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.material import Material, Tag, Experience
from app.utils.file_parser import parse_file
from app.utils.llm_client import get_llm_client
from app.config import settings

logger = logging.getLogger(__name__)


class MaterialService:

    async def upload_and_parse(self, file_path: str, title: str,
                               category: str = "general", tags: List[str] = None,
                               db: Session = None) -> Material:
        """上传并解析简历文件"""
        # 读取文件文本
        raw_text = parse_file(file_path)

        # 用LLM解析结构化数据
        structured = {}
        try:
            structured = await get_llm_client().parse_resume(raw_text)
        except Exception as e:
            logger.warning(f"LLM解析失败，将保存原始文本: {e}")

        # 保存文件到素材目录
        os.makedirs(settings.RESUME_DIR, exist_ok=True)
        ext = os.path.splitext(file_path)[1]
        dest_path = os.path.join(settings.RESUME_DIR, f"{title}_{id(self)}{ext}")
        shutil.copy2(file_path, dest_path)

        # 创建素材记录
        material = Material(
            title=title,
            file_type=ext.lstrip("."),
            file_path=dest_path,
            raw_text=raw_text,
            structured_data=json.dumps(structured, ensure_ascii=False),
            category=category,
            source="upload",
        )

        # 处理标签
        if tags and db:
            for tag_name in tags:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.flush()
                material.tags.append(tag)

        db.add(material)
        db.commit()
        db.refresh(material)
        return material

    def get_material(self, material_id: int, db: Session) -> Optional[Material]:
        return db.query(Material).filter(Material.id == material_id).first()

    def list_materials(self, category: str = None, tag: str = None,
                       page: int = 1, page_size: int = 20,
                       db: Session = None):
        query = db.query(Material)
        if category:
            query = query.filter(Material.category == category)
        if tag:
            query = query.join(Material.tags).filter(Tag.name == tag)
        total = query.count()
        items = query.order_by(Material.updated_at.desc()).offset(
            (page - 1) * page_size).limit(page_size).all()
        return items, total

    def delete_material(self, material_id: int, db: Session) -> bool:
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            return False
        # 删除物理文件
        if material.file_path and os.path.exists(material.file_path):
            os.remove(material.file_path)
        db.delete(material)
        db.commit()
        return True

    def create_tag(self, name: str, color: str = "#409EFF", db: Session = None) -> Tag:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name, color=color)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        return tag

    def list_tags(self, db: Session = None):
        tags = db.query(Tag).all()
        result = []
        for tag in tags:
            result.append({
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "material_count": len(tag.materials),
                "created_at": tag.created_at,
            })
        return result

    async def optimize_experience(self, exp_id: int,
                                  jd_keywords: list = None,
                                  db: Session = None) -> Experience:
        """优化经历为STAR描述"""
        exp = db.query(Experience).filter(Experience.id == exp_id).first()
        if not exp:
            raise ValueError("经历不存在")

        result = await get_llm_client().generate_star_description(
            exp.original_desc or "", jd_keywords
        )
        exp.star_desc = result.get("star_desc")
        exp.skills = json.dumps(result.get("skills_used", []), ensure_ascii=False)
        exp.achievements = json.dumps(result.get("achievements", {}), ensure_ascii=False)
        db.commit()
        db.refresh(exp)
        return exp


material_service = MaterialService()
