# 导入 Pydantic 配置基类。
from pydantic_settings import BaseSettings, SettingsConfigDict


# 定义应用运行配置。
class Settings(BaseSettings):
    # 设置应用名称默认值。
    app_name: str = "fastapi-scaffold"
    # 设置 SQLite 数据库连接地址默认值。
    database_url: str = "sqlite:///./data/app.db"
    # 设置 JWT 开发环境签名密钥默认值。
    jwt_secret_key: str = "change-this-development-secret-key"
    # 设置 JWT 访问令牌有效分钟数默认值。
    jwt_expire_minutes: int = 30
    # 设置 OpenAI 兼容 API 基础地址。
    llm_base_url: str = "https://api.openai.com/v1"
    # 设置 OpenAI 兼容 API 密钥。
    llm_api_key: str = ""
    # 设置默认调用模型名称。
    llm_model: str = "gpt-4o-mini"
    # 设置模型调用超时秒数。
    llm_timeout_seconds: float = 60.0
    # 配置从项目环境文件和环境变量加载字段值。
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# 创建全局应用配置实例。
settings = Settings()
