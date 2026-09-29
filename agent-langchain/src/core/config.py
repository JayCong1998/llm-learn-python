# 导入环境配置基类与读取规则。
from pydantic_settings import BaseSettings, SettingsConfigDict

# SettingsConfigDict 让 Pydantic Settings 从 .env 和系统环境变量读取配置；
# 如果某个字段都没有对应配置，就使用字段声明的默认值。

# 集中定义应用运行时配置。
class Settings(BaseSettings):
    # 从项目环境文件读取配置项。
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 设置服务展示名称。
    app_name: str = "Agent LangChain"
    # 控制 FastAPI 调试模式。
    debug: bool = True
    # 保存 DashScope API 密钥。
    dashscope_api_key: str = ""
    # 指定默认 Qwen 模型名称。
    qwen_model: str = "qwen-plus"
    # 指定 DashScope 的 OpenAI 兼容接口地址。
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"


# 构造供应用各模块共享的配置对象。
settings = Settings()
