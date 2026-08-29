"""Minimal LangChain model call with environment-based configuration."""

# 导入不可变数据类装饰器。
from dataclasses import dataclass
# 导入读取环境变量的标准库。
import os
# 导入用于定位项目配置文件的路径工具。
from pathlib import Path

# 导入加载 dotenv 配置文件的函数。
from dotenv import load_dotenv
# 导入 LangChain 的 OpenAI 聊天模型封装。
from langchain_openai import ChatOpenAI


# 定义配置缺失时抛出的专用异常。
class ConfigurationError(ValueError):
    """Raised when the project cannot find required configuration."""


# 将设置对象定义为不可变数据类。
@dataclass(frozen=True)
# 定义保存模型配置的数据结构。
class Settings:
    # 声明 API 密钥字段。
    api_key: str
    # 声明模型名称字段。
    model: str
    # 声明 OpenAI 兼容服务的基础地址字段。
    base_url: str


# 定义读取并校验模型配置的函数。
def get_settings() -> Settings:
    """Load this project's .env file and return model settings."""
    # 加载当前项目目录中的 .env 文件。
    load_dotenv(Path(__file__).with_name(".env"))
    # 读取 OpenAI API 密钥。
    api_key = os.getenv("OPENAI_API_KEY")
    # 在未配置密钥时终止后续模型调用。
    if not api_key:
        # 提示用户创建配置文件并填写密钥。
        raise ConfigurationError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    # 读取 OpenAI 兼容服务的基础地址。
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    # 返回密钥、模型名称和服务地址组成的配置对象。
    return Settings(
        api_key=api_key,
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        base_url=base_url,
    )


# 定义向聊天模型提问的函数。
def ask_question(question: str) -> str:
    """Send one question to the configured chat model."""
    # 获取已经校验过的模型配置。
    settings = get_settings()
    # 使用配置创建指向指定服务端点的 LangChain 聊天模型实例。
    model = ChatOpenAI(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
    )
    # 调用模型并将回复内容转换为字符串。
    return str(model.invoke(question).content)
