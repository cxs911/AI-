"""投递管理服务 - 投递执行、风控、统计"""
import logging
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.delivery import DeliveryJob, DeliveryRecord, DeliveryStats, RiskControl
from app.utils.selenium_client import BossSeleniumClient
from app.config import settings

logger = logging.getLogger(__name__)


class DeliveryService:

    def __init__(self):
        self.boss_client: Optional[BossSeleniumClient] = None

    def get_boss_client(self) -> BossSeleniumClient:
        """获取或创建Boss客户端单例"""
        if not self.boss_client:
            self.boss_client = BossSeleniumClient()
        return self.boss_client

    def save_jobs(self, jobs: list, db: Session = None) -> List[DeliveryJob]:
        """保存抓取的岗位到投递列表"""
        saved = []
        for job in jobs:
            existing = db.query(DeliveryJob).filter(
                DeliveryJob.job_id == job.get("job_id", "")
            ).first()
            if existing:
                continue

            delivery_job = DeliveryJob(
                job_id=job.get("job_id", ""),
                title=job.get("title", ""),
                company=job.get("company", ""),
                city=job.get("city", "北京"),
                salary_min=job.get("salary_min", 0),
                salary_max=job.get("salary_max", 0),
                salary_str=job.get("salary", ""),
                tags=job.get("tags", []),
                url=job.get("url", ""),
                match_score=job.get("match_score", 0),
                boss_info={
                    "name": job.get("boss_name", ""),
                    "title": job.get("boss_title", ""),
                },
                need_manual_review=1,
            )
            db.add(delivery_job)
            db.flush()
            saved.append(delivery_job)

        db.commit()
        return saved

    def list_delivery_jobs(self, status: str = None, is_filtered: int = None,
                           page: int = 1, page_size: int = 20,
                           db: Session = None):
        query = db.query(DeliveryJob)
        if status:
            query = query.filter(DeliveryJob.delivery_status == status)
        if is_filtered is not None:
            query = query.filter(DeliveryJob.is_filtered == is_filtered)
        total = query.count()
        items = query.order_by(DeliveryJob.created_at.desc()).offset(
            (page - 1) * page_size).limit(page_size).all()
        return items, total

    async def deliver_single(self, job_id: int, greeting: str = "",
                             db: Session = None) -> bool:
        """手动投递单个岗位"""
        job = db.query(DeliveryJob).filter(DeliveryJob.id == job_id).first()
        if not job:
            raise ValueError("岗位不存在")

        client = self.get_boss_client()
        if not client.driver:
            raise Exception("浏览器未启动，请先在浏览器管理中启动")

        success = client.deliver_job(job.url or "", greeting)
        if success:
            job.delivery_status = "delivered"
            job.delivered_at = datetime.now()
            # 记录
            record = DeliveryRecord(
                delivery_job_id=job_id,
                action="deliver",
                detail="手动投递成功",
            )
            db.add(record)
            # 更新统计
            self._update_stats(db)
        else:
            record = DeliveryRecord(
                delivery_job_id=job_id,
                action="deliver",
                detail=f"投递失败: {'触发了人机验证' if client.is_paused else '未知错误'}",
            )
            db.add(record)

        db.commit()
        return success

    async def deliver_batch(self, job_ids: List[int],
                            enable_review: bool = False,
                            db: Session = None) -> dict:
        """批量投递"""
        if not enable_review:
            raise ValueError("请开启【人工审核开关】才能批量投递")

        results = {"success": 0, "failed": 0, "skipped": 0}
        client = self.get_boss_client()

        if not client.driver:
            raise Exception("浏览器未启动")

        for job_id in job_ids:
            # 检查是否暂停
            if client.is_paused:
                logger.warning("检测到人机验证，投递已暂停")
                break

            # 检查投递上限
            if not client._check_delivery_limit():
                logger.warning("已达每日投递上限")
                break

            job = db.query(DeliveryJob).filter(DeliveryJob.id == job_id).first()
            if not job or job.delivery_status == "delivered":
                results["skipped"] += 1
                continue

            success = client.deliver_job(job.url or "", job.greeting or "")
            if success:
                job.delivery_status = "delivered"
                job.delivered_at = datetime.now()
                results["success"] += 1
            else:
                results["failed"] += 1

            db.commit()

        # 更新统计
        self._update_stats(db)
        return results

    def _update_stats(self, db: Session = None):
        """更新当日投递统计"""
        today = date.today().isoformat()
        stats = db.query(DeliveryStats).filter(
            DeliveryStats.date == today
        ).first()
        if not stats:
            stats = DeliveryStats(date=today)
            db.add(stats)

        stats.total_deliveries = db.query(DeliveryJob).filter(
            DeliveryJob.delivery_status == "delivered",
        ).count()
        stats.reads = db.query(DeliveryJob).filter(
            DeliveryJob.delivery_status == "replied"
        ).count()
        db.commit()

    def get_stats(self, days: int = 7, db: Session = None):
        """获取投递统计"""
        from datetime import timedelta
        start_date = (date.today() - timedelta(days=days)).isoformat()
        stats = db.query(DeliveryStats).filter(
            DeliveryStats.date >= start_date
        ).order_by(DeliveryStats.date).all()
        return stats

    def start_browser(self):
        """启动浏览器"""
        client = self.get_boss_client()
        client.start_driver()

    def wait_login(self, timeout: int = 120) -> bool:
        """等待登录"""
        client = self.get_boss_client()
        return client.wait_for_login(timeout)

    def close_browser(self):
        """关闭浏览器"""
        if self.boss_client:
            self.boss_client.quit()
            self.boss_client = None

    def update_risk_config(self, key: str, value: str,
                           description: str = "", db: Session = None):
        """更新风控配置"""
        config = db.query(RiskControl).filter(RiskControl.key == key).first()
        if config:
            config.value = value
        else:
            config = RiskControl(key=key, value=value, description=description)
            db.add(config)
        db.commit()
        return config


delivery_service = DeliveryService()
