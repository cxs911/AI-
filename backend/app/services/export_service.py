"""简历导出服务 - ATS标准PDF导出"""
import os
import json
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.resume import GeneratedResume
from app.config import settings

logger = logging.getLogger(__name__)


class ExportService:

    def export_pdf(self, resume_id: int, db: Session = None) -> str:
        """导出ATS标准PDF简历"""
        resume = db.query(GeneratedResume).filter(
            GeneratedResume.id == resume_id
        ).first()
        if not resume:
            raise ValueError("简历不存在")

        # 生成HTML内容
        html = self._resume_to_html(resume)

        # 导出为PDF
        os.makedirs(settings.EXPORT_DIR, exist_ok=True)
        output_path = os.path.join(
            settings.EXPORT_DIR,
            f"resume_{resume.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        # 使用WeasyPrint将HTML转为PDF
        try:
            from weasyprint import HTML
            HTML(string=html).write_pdf(output_path)
            logger.info(f"PDF导出成功: {output_path}")
        except Exception as e:
            logger.warning(f"WeasyPrint导出失败，尝试备用方案: {e}")
            # 备用: 保存为HTML
            output_path = output_path.replace(".pdf", ".html")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)

        return output_path

    def _resume_to_html(self, resume: GeneratedResume) -> str:
        """将简历对象转换为HTML"""
        sections = []

        # 个人信息
        personal = resume.personal_info or {}
        name = personal.get("name", "姓名")
        phone = personal.get("phone", "")
        email = personal.get("email", "")
        location = personal.get("location", "")

        sections.append(f"""
        <div class="header">
            <h1>{name}</h1>
            <div class="contact">
                {f'<span>📞 {phone}</span>' if phone else ''}
                {f'<span>✉️ {email}</span>' if email else ''}
                {f'<span>📍 {location}</span>' if location else ''}
            </div>
        </div>
        """)

        # 个人总结
        if resume.summary:
            sections.append(f"""
            <div class="section">
                <h2>个人总结</h2>
                <p>{resume.summary}</p>
            </div>
            """)

        # 技能
        skills = resume.skills or []
        if skills:
            skills_html = "".join([f'<span class="skill-tag">{s}</span>' for s in skills])
            sections.append(f"""
            <div class="section">
                <h2>技能</h2>
                <div class="skills">{skills_html}</div>
            </div>
            """)

        # 工作经历
        experiences = resume.work_experience or []
        if experiences:
            exp_html = ""
            for exp in experiences:
                if isinstance(exp, str):
                    exp = json.loads(exp) if exp.startswith("{") else {"description": exp}
                exp_html += f"""
                <div class="exp-item">
                    <div class="exp-header">
                        <span class="exp-title">{exp.get('title', '')}</span>
                        <span class="exp-company">{exp.get('company', '')}</span>
                        <span class="exp-date">{exp.get('start_date', '')} - {exp.get('end_date', '')}</span>
                    </div>
                    <p class="exp-desc">{exp.get('description', '')}</p>
                </div>
                """

            sections.append(f"""
            <div class="section">
                <h2>工作经历</h2>
                {exp_html}
            </div>
            """)

        # 匹配度
        if resume.match_score:
            sections.append(f"""
            <div class="section match-info">
                <h2>岗位匹配度</h2>
                <div class="match-score">匹配度: {resume.match_score}%</div>
            </div>
            """)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{name} - 简历</title>
<style>
    @page {{
        size: A4;
        margin: 20mm 15mm;
    }}
    body {{
        font-family: "Microsoft YaHei", "SimSun", Arial, sans-serif;
        font-size: 12pt;
        line-height: 1.6;
        color: #333;
        max-width: 210mm;
    }}
    .header {{
        text-align: center;
        border-bottom: 2px solid #2c3e50;
        padding-bottom: 15px;
        margin-bottom: 20px;
    }}
    .header h1 {{
        font-size: 24pt;
        color: #2c3e50;
        margin: 0 0 10px 0;
    }}
    .contact {{
        font-size: 10pt;
        color: #666;
    }}
    .contact span {{
        margin: 0 10px;
    }}
    .section {{
        margin-bottom: 15px;
    }}
    .section h2 {{
        font-size: 14pt;
        color: #2c3e50;
        border-bottom: 1px solid #ddd;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }}
    .skills {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }}
    .skill-tag {{
        background: #e8f4f8;
        padding: 3px 10px;
        border-radius: 3px;
        font-size: 10pt;
    }}
    .exp-item {{
        margin-bottom: 12px;
    }}
    .exp-header {{
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }}
    .exp-title {{
        font-weight: bold;
        font-size: 11pt;
    }}
    .exp-company {{
        color: #666;
        font-size: 10pt;
    }}
    .exp-date {{
        color: #999;
        font-size: 9pt;
    }}
    .exp-desc {{
        margin: 5px 0 0 0;
        font-size: 10pt;
    }}
    .match-info {{
        background: #f0f8ff;
        padding: 10px;
        border-radius: 5px;
    }}
    .match-score {{
        font-size: 14pt;
        font-weight: bold;
        color: #27ae60;
    }}
    @media print {{
        body {{
            margin: 0;
            padding: 0;
        }}
    }}
</style>
</head>
<body>
    {"".join(sections)}
</body>
</html>"""
        return html


export_service = ExportService()
