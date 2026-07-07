"""应用配置"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "AI JD简历适配系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite:///./data/jd_resume.db"

    # LLM 供应商选择: "ollama" 或 "deepseek"
    LLM_PROVIDER: str = "deepseek"  # 默认使用 DeepSeek

    # Ollama 配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    OLLAMA_TIMEOUT: int = 120

    # DeepSeek 配置 (OpenAI 兼容格式)
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # 文件存储
    UPLOAD_DIR: str = "./data/uploads"
    RESUME_DIR: str = "./data/resumes"
    EXPORT_DIR: str = "./data/exports"

    # Boss 配置
    BOSS_DELIVERY_LIMIT: int = 25  # 每日投递上限
    BOSS_MIN_INTERVAL: int = 15    # 最小投递间隔(秒)
    BOSS_MAX_INTERVAL: int = 40    # 最大投递间隔(秒)
    BOSS_STAY_MIN: int = 3         # 页面最短停留(秒)
    BOSS_STAY_MAX: int = 12        # 页面最长停留(秒)
    BOSS_WORK_START: str = "09:00" # 工作开始时间
    BOSS_WORK_END: str = "18:00"   # 工作结束时间
    BOSS_WORK_DAYS: str = "1,2,3,4,5"  # 工作日 1=周一

    # 风控
    RISK_CAPTCHA_PAUSE: bool = True  # 人机验证自动暂停

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
