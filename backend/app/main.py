"""FastAPI 主应用入口"""
import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db

# 配置日志
os.makedirs("./data/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("./data/logs/app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    # 创建数据目录
    os.makedirs("./data", exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.RESUME_DIR, exist_ok=True)
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)
    os.makedirs("./data/chrome_profile", exist_ok=True)
    os.makedirs("./data/logs", exist_ok=True)

    # 初始化数据库
    init_db()
    logger.info("数据库初始化完成")

    # 挂载静态文件
    export_path = Path(settings.EXPORT_DIR).resolve()
    export_path.mkdir(parents=True, exist_ok=True)
    app.mount("/api/files", StaticFiles(directory=str(export_path)), name="exports")
    logger.info(f"静态文件服务已挂载: {export_path}")

    yield
    logger.info("应用关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI JD简历适配系统 - 本地私有化部署",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from app.routers import material, jd, resume, delivery, settings as settings_router

app.include_router(material.router)
app.include_router(jd.router)
app.include_router(resume.router)
app.include_router(delivery.router)
app.include_router(settings_router.router)

# 用户认证（自动创建默认账号 admin/admin123）
from app.routers import auth as auth_router
app.include_router(auth_router.router)


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
