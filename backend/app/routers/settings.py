"""系统设置 API路由 - LLM配置、模型管理"""
import json
import logging
from fastapi import APIRouter, Body
from app.config import settings as app_settings
from app.utils.llm_client import LLMClient, _load_saved_config, _save_config
from app.schemas.common import ResponseBase

router = APIRouter(prefix="/api/settings", tags=["系统设置"])
logger = logging.getLogger(__name__)


@router.get("/llm", response_model=ResponseBase)
def get_llm_config():
    """获取 LLM 配置（含 provider 和所有供应商的参数，优先使用持久化配置）"""
    saved = _load_saved_config()
    return ResponseBase(data={
        "provider": saved.get("provider") or app_settings.LLM_PROVIDER,
        # Ollama
        "ollama_base_url": saved.get("ollama_base_url") or app_settings.OLLAMA_BASE_URL,
        "ollama_model": saved.get("ollama_model") or app_settings.OLLAMA_MODEL,
        "ollama_timeout": saved.get("ollama_timeout") or app_settings.OLLAMA_TIMEOUT,
        # DeepSeek
        "deepseek_base_url": saved.get("deepseek_base_url") or app_settings.DEEPSEEK_BASE_URL,
        "deepseek_model": saved.get("deepseek_model") or app_settings.DEEPSEEK_MODEL,
        "deepseek_api_key": mask_api_key(
            saved.get("deepseek_api_key") or app_settings.DEEPSEEK_API_KEY
        ),
        "has_api_key": bool(saved.get("deepseek_api_key") or app_settings.DEEPSEEK_API_KEY),
    })


def mask_api_key(key: str) -> str:
    """脱敏显示 API Key"""
    if not key or len(key) < 8:
        return ""
    return key[:6] + "*" * (len(key) - 8) + key[-2:]


@router.post("/llm/test", response_model=ResponseBase)
async def test_llm_connection(
    provider: str = Body(...),
    base_url: str = Body(""),
    model: str = Body(""),
    api_key: str = Body(""),
):
    """测试 LLM 连接（支持 Ollama / DeepSeek）"""
    try:
        # 如果 key 为空或已被掩盖，从已保存配置读取真实 Key
        if provider == "deepseek" and (not api_key or "*" in api_key):
            saved = _load_saved_config()
            api_key = saved.get("deepseek_api_key", "")

        client = LLMClient(
            provider=provider,
            base_url=base_url or None,
            model=model or None,
            api_key=api_key or None,
            use_saved=False,
        )
        content = await client.chat([
            {"role": "user", "content": "回复'连接成功'四个字"}
        ])
        return ResponseBase(data={"response": content})
    except Exception as e:
        logger.warning(f"LLM 连接测试失败: {e}")
        return ResponseBase(code=400, message=f"连接失败: {str(e)}")


@router.post("/llm/save", response_model=ResponseBase)
def save_llm_config(
    provider: str = Body(...),
    deepseek_api_key: str = Body(""),
    deepseek_base_url: str = Body(""),
    deepseek_model: str = Body(""),
    ollama_base_url: str = Body(""),
    ollama_model: str = Body(""),
    ollama_timeout: int = Body(120),
):
    """保存 LLM 配置到持久化文件"""
    try:
        data = {"provider": provider}
        if provider == "deepseek":
            if deepseek_api_key:
                data["deepseek_api_key"] = deepseek_api_key
            if deepseek_base_url:
                data["deepseek_base_url"] = deepseek_base_url
            if deepseek_model:
                data["deepseek_model"] = deepseek_model
        else:
            if ollama_base_url:
                data["ollama_base_url"] = ollama_base_url
            if ollama_model:
                data["ollama_model"] = ollama_model
            if ollama_timeout:
                data["ollama_timeout"] = ollama_timeout

        if _save_config(data):
            logger.info(f"LLM 配置已保存 (provider: {provider})")
            return ResponseBase(message=f"配置已保存（{provider}）")
        return ResponseBase(code=500, message="保存配置失败")
    except Exception as e:
        logger.error(f"保存 LLM 配置出错: {e}")
        return ResponseBase(code=500, message=f"保存失败: {str(e)}")


@router.get("/llm/models", response_model=ResponseBase)
async def list_llm_models(provider: str = "ollama", base_url: str = ""):
    """获取可用的模型列表（仅 Ollama 支持）"""
    if provider == "deepseek":
        return ResponseBase(data=[
            {"name": "deepseek-chat"},
            {"name": "deepseek-reasoner"},
        ])
    try:
        import httpx
        url = base_url or app_settings.OLLAMA_BASE_URL
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = [{"name": m["name"]} for m in data.get("models", [])]
            return ResponseBase(data=models)
    except Exception as e:
        return ResponseBase(code=400, message=f"获取失败: {str(e)}")


@router.get("/system", response_model=ResponseBase)
def get_system_info():
    """获取系统信息"""
    import os
    return ResponseBase(data={
        "app_name": app_settings.APP_NAME,
        "version": app_settings.APP_VERSION,
        "provider": app_settings.LLM_PROVIDER,
        "db_path": app_settings.DATABASE_URL,
        "upload_dir": app_settings.UPLOAD_DIR,
        "export_dir": app_settings.EXPORT_DIR,
        "delivery_limit": app_settings.BOSS_DELIVERY_LIMIT,
        "work_hours": f"{app_settings.BOSS_WORK_START}-{app_settings.BOSS_WORK_END}",
        "work_days": app_settings.BOSS_WORK_DAYS,
    })
