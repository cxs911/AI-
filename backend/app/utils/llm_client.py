"""大模型客户端 - 支持 Ollama 本地 / DeepSeek 在线 API"""
import json
import os
import httpx
import logging
from typing import Optional, List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

# 持久化配置文件路径 (放在 data 目录下，和数据库同一层级)
_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
CONFIG_FILE = os.path.abspath(os.path.join(_CONFIG_DIR, "llm_config.json"))


def _load_saved_config() -> dict:
    """从持久化文件读取 LLM 配置"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"读取 LLM 配置文件失败: {e}")
    return {}


def _save_config(data: dict):
    """保存 LLM 配置到持久化文件"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        # 合并现有配置
        existing = _load_saved_config()
        existing.update(data)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存 LLM 配置失败: {e}")
        return False


class LLMClient:
    """统一大模型客户端，支持 Ollama 和 DeepSeek (OpenAI 兼容格式)"""

    def __init__(self, provider: str = None,
                 base_url: str = None, model: str = None,
                 api_key: str = None, timeout: int = None,
                 use_saved: bool = True):
        # 优先使用传入参数，其次保存的配置，最后 .env 默认值
        saved = _load_saved_config() if use_saved else {}

        self.provider = provider or saved.get("provider") or settings.LLM_PROVIDER
        self.provider = self.provider.lower()
        self.timeout = timeout or saved.get("timeout") or settings.OLLAMA_TIMEOUT

        if self.provider == "deepseek":
            self.base_url = (base_url or saved.get("deepseek_base_url") or
                             settings.DEEPSEEK_BASE_URL).rstrip("/")
            self.model = model or saved.get("deepseek_model") or settings.DEEPSEEK_MODEL
            self.api_key = api_key or saved.get("deepseek_api_key") or settings.DEEPSEEK_API_KEY
        else:
            self.base_url = (base_url or saved.get("ollama_base_url") or
                             settings.OLLAMA_BASE_URL).rstrip("/")
            self.model = model or saved.get("ollama_model") or settings.OLLAMA_MODEL
            self.api_key = api_key or ""

    async def chat(self, messages: List[Dict[str, str]],
                   temperature: float = 0.1,
                   format_json: bool = False) -> str:
        """调用大模型对话接口"""
        if self.provider == "deepseek":
            return await self._chat_deepseek(messages, temperature, format_json)
        else:
            return await self._chat_ollama(messages, temperature, format_json)

    async def _chat_deepseek(self, messages: List[Dict[str, str]],
                              temperature: float = 0.1,
                              format_json: bool = False) -> str:
        """调用 DeepSeek API (OpenAI 兼容格式)"""
        if not self.api_key:
            raise Exception(
                "DeepSeek API Key 未设置，请在 系统设置 -> DeepSeek 配置 中填入 API Key"
            )

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        # DeepSeek 不支持 response_format，通过 prompt 控制

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code == 401:
                    detail = resp.text[:200]
                    raise Exception(
                        f"DeepSeek API Key 无效，服务器拒绝认证 (HTTP 401)。"
                        f"请检查: ① Key 是否填写正确 ② Key 是否已过期 ③ 账户余额是否充足"
                    )
                resp.raise_for_status()
                result = resp.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("DeepSeek API Key 无效，请检查后在设置中更新")
            elif e.response.status_code == 429:
                raise Exception("DeepSeek API 请求过于频繁，请稍后再试")
            raise Exception(f"DeepSeek API 调用失败 (HTTP {e.response.status_code}): {e.response.text[:200]}")
        except httpx.TimeoutException:
            raise Exception("DeepSeek API 请求超时，请检查网络连接")
        except Exception as e:
            raise Exception(f"DeepSeek 调用失败: {str(e)}")

    async def _chat_ollama(self, messages: List[Dict[str, str]],
                            temperature: float = 0.1,
                            format_json: bool = False) -> str:
        """调用 Ollama 接口"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if format_json:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                result = resp.json()
                return result.get("message", {}).get("content", "")
        except httpx.ConnectError:
            raise Exception(
                f"Ollama 连接失败，请确保 Ollama 服务已启动。当前地址: {self.base_url}"
            )
        except Exception as e:
            raise Exception(f"Ollama 调用失败: {str(e)}。当前地址: {self.base_url}")

    async def extract_json(self, messages: List[Dict[str, str]],
                           temperature: float = 0.05) -> dict:
        """调用并解析 JSON 响应"""
        content = await self.chat(messages, temperature=temperature, format_json=True)
        return self._parse_json(content)

    def _parse_json(self, content: str) -> dict:
        """从模型返回内容中提取 JSON"""
        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        # 尝试从 markdown 代码块提取
        import re
        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # 尝试找第一个 { 到最后一个 }
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end > start:
            try:
                return json.loads(content[start:end + 1])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"模型返回非 JSON 格式: {content[:300]}")

    # ====== 以下是各种业务 Prompt ======

    async def parse_resume(self, raw_text: str) -> dict:
        """解析简历文本为结构化数据"""
        prompt = f"""你是一个专业的简历解析助手。请从以下简历文本中提取结构化信息，输出JSON格式。

简历文本：
{raw_text[:8000]}

请解析为以下JSON结构：
{{
  "name": "姓名",
  "phone": "电话",
  "email": "邮箱",
  "education": [
    {{"school": "学校", "degree": "学历", "major": "专业", "start_date": "开始时间", "end_date": "结束时间"}}
  ],
  "work_experience": [
    {{"company": "公司", "title": "职位", "start_date": "开始时间", "end_date": "结束时间", "description": "工作描述", "achievements": ["成果1", "成果2"]}}
  ],
  "skills": ["技能1", "技能2"],
  "summary": "个人总结"
}}

注意：只输出JSON，不要其他说明。未找到的字段设为null或空数组。"""
        return await self.extract_json([
            {"role": "system", "content": "你是简历解析专家，擅长从文本提取结构化信息。"},
            {"role": "user", "content": prompt}
        ])

    async def analyze_jd(self, jd_text: str) -> dict:
        """解析JD，提取核心能力和权重"""
        prompt = f"""请分析以下岗位描述(JD)，提取核心能力要求并打分。

JD文本：
{jd_text[:6000]}

输出以下JSON格式：
{{
  "core_skills": [
    {{"name": "技能名称", "weight": 权重1-100, "level": "精通/熟练/了解", "description": "具体要求"}}
  ],
  "soft_skills": [
    {{"name": "软性能力", "description": "具体要求"}}
  ],
  "responsibilities": [
    {{"item": "职责描述", "importance": "核心/重要/一般"}}
  ],
  "keywords": ["关键词1", "关键词2"],
  "total_score": 综合评分0-100,
  "industry": "行业领域"
}}

注意：只输出JSON。权重反映JD中对各项技能的重视频率和要求深度。"""
        return await self.extract_json([
            {"role": "system", "content": "你是JD分析专家，擅长能力拆解和权重评估。"},
            {"role": "user", "content": prompt}
        ])

    async def generate_star_description(self, original_desc: str, jd_keywords: list = None) -> dict:
        """将原始经历转化为STAR量化描述"""
        keywords_hint = ""
        if jd_keywords:
            keywords_hint = f"请自然融入以下关键词: {', '.join(jd_keywords[:10])}"

        prompt = f"""请将以下经历描述改写成STAR格式(Situation-Task-Action-Result)的职场化描述，要求数据量化、突出成果，绝不虚构经历内容。

原始描述：
{original_desc}

{keywords_hint}

输出JSON：
{{
  "star_desc": "完整的STAR描述，包含时间、背景、任务、行动和量化结果",
  "skills_used": ["使用的技能1", "技能2"],
  "achievements": {{"metric1": "具体数值或成果", "metric2": "..."}},
  "highlight_points": ["亮点1", "亮点2"]
}}

注意：只输出JSON。可以在原始事实基础上优化表述和量化，但不能编造不存在的经历。"""
        return await self.extract_json([
            {"role": "system", "content": "你是简历优化专家，擅长STAR法则量化表达。"},
            {"role": "user", "content": prompt}
        ])

    async def generate_resume(self, user_info: dict, jd_analysis: dict,
                              star_experiences: list, style: str = "professional") -> dict:
        """根据JD生成定制简历"""
        prompt = f"""请根据以下信息生成一份针对特定岗位的定制简历内容。

【个人信息】
{json.dumps(user_info, ensure_ascii=False, indent=2)}

【JD分析 - 核心要求】
{json.dumps(jd_analysis, ensure_ascii=False, indent=2)}

【经历库】
{json.dumps(star_experiences, ensure_ascii=False, indent=2)}

【要求】
1. 根据JD要求动态调整经历模块的排序和侧重点，把最相关的经历放前面
2. ST描述要融入JD关键词，但保持真实
3. 个人总结要针对JD定制，突出匹配度
4. 技能标签要匹配JD要求

输出JSON：
{{
  "summary": "针对JD定制的个人总结(150字内)",
  "work_experience": [
    {{"company": "", "title": "", "start_date": "", "end_date": "",
      "description": "STAR描述，数据量化",
      "relevance": "与JD的关联说明"}}
  ],
  "skills": ["技能标签按JD权重排序"],
  "section_order": ["summary", "skills", "experience", "education"],
  "match_analysis": "与JD的匹配点说明"
}}

注意：只输出JSON。"""
        return await self.extract_json([
            {"role": "system", "content": "你是资深HR和简历优化专家，擅长定制化简历生成。"},
            {"role": "user", "content": prompt}
        ])

    async def generate_greeting(self, resume_info: dict, job_info: dict,
                                style: str = "fresh") -> str:
        """生成一对一招呼语"""
        style_hint = "应届生/校招风格，谦虚诚恳，突出学习能力和专业基础" if style == "fresh" else "社招风格，自信专业，突出经验和匹配度"

        prompt = f"""请为Boss直聘生成一段一对一的招呼语（打招呼消息）。

【求职者信息】
{json.dumps(resume_info, ensure_ascii=False, indent=2)}

【岗位信息】
{json.dumps(job_info, ensure_ascii=False, indent=2)}

【要求】
- {style_hint}
- 称呼对方为"您好"
- 简短自我介绍（姓名+核心匹配点）
- 表达对岗位的兴趣
- 询问是否可以进一步沟通
- 不超过100字
- 不要使用模板化表达，要像真人写的

直接输出招呼语文本，不要JSON，不要其他说明。"""
        content = await self.chat([
            {"role": "system", "content": "你是求职沟通专家，擅长写自然的招呼语。"},
            {"role": "user", "content": prompt}
        ], temperature=0.7)
        return content.strip().strip('"')

    async def calculate_match_score(self, resume_data: dict, jd_data: dict) -> dict:
        """计算简历与JD的匹配度"""
        prompt = f"""请评估以下简历与岗位的匹配度。

【简历摘要】
{json.dumps(resume_data, ensure_ascii=False, indent=2)}

【JD要求】
{json.dumps(jd_data, ensure_ascii=False, indent=2)}

输出JSON：
{{
  "total_score": 0-100的综合匹配分,
  "skill_match": {{"matched": ["匹配技能"], "missing": ["缺失技能"], "score": 技能匹配分0-100}},
  "experience_match": {{"score": 经验匹配分0-100, "analysis": "分析"}},
  "edu_match": {{"score": 学历匹配分0-100, "analysis": "分析"}},
  "overall_analysis": "整体匹配分析",
  "suggestions": ["改进建议1", "改进建议2"]
}}
注意：只输出JSON。评分要严格，不要虚高。"""
        return await self.extract_json([
            {"role": "system", "content": "你是招聘匹配专家，擅长精准评估人岗匹配度。"},
            {"role": "user", "content": prompt}
        ])

    async def filter_outsource_jobs(self, job_info: dict) -> dict:
        """过滤外包/培训/诈骗岗位"""
        prompt = f"""请判断以下岗位是否为外包、培训、虚假招聘或诈骗岗位，给出审核意见。

岗位信息：
{json.dumps(job_info, ensure_ascii=False, indent=2)}

输出JSON：
{{
  "is_filter": true/false,
  "reason": "过滤原因(如果不通过)",
  "confidence": 0-100,
  "category": "外包/培训/虚假/正常"
}}
注意：只输出JSON，严格审核。"""
        return await self.extract_json([
            {"role": "system", "content": "你是招聘安全审核专家，擅长识别风险岗位。"},
            {"role": "user", "content": prompt}
        ])


# 全局单例（懒加载模式）
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取 LLM 客户端（每次读取最新配置，优先使用持久化配置）"""
    global _llm_client
    saved = _load_saved_config()
    provider = saved.get("provider") or settings.LLM_PROVIDER

    if _llm_client is None or _llm_client.provider != provider:
        _llm_client = LLMClient(
            provider=provider,
            use_saved=True,
        )
        logger.info(f"LLM 客户端已切换至 {'DeepSeek' if provider == 'deepseek' else 'Ollama'} "
                    f"(模型: {_llm_client.model})")
    return _llm_client


# 兼容旧代码的全局实例
llm_client = get_llm_client()
