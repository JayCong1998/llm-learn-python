# 导入 HTTP 客户端。
import httpx
# 导入应用配置。
from app.core.config import settings

# 封装 OpenAI 兼容聊天补全调用。
class LlmClient:
    # 调用模型并返回内容与用量。
    def chat(self, messages: list[dict[str, str]]) -> tuple[str, int, int]:
        # 发起兼容聊天补全请求。
        response = httpx.post(f"{settings.llm_base_url.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {settings.llm_api_key}"}, json={"model": settings.llm_model, "messages": messages}, timeout=settings.llm_timeout_seconds)
        # 检查远端响应状态。
        response.raise_for_status()
        # 读取响应数据。
        payload = response.json()
        # 返回模型内容及令牌统计。
        return payload["choices"][0]["message"]["content"], payload.get("usage", {}).get("prompt_tokens", 0), payload.get("usage", {}).get("completion_tokens", 0)
