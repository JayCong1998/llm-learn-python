"""提示词工程示例的模型配置和调用工具。"""

# 导入不可变数据类装饰器。
from dataclasses import dataclass
# 导入读取环境变量的标准库。
import os
# 导入定位项目配置文件的路径工具。
from pathlib import Path

# 导入加载 dotenv 配置文件的函数。
from dotenv import load_dotenv
# 导入 LangChain 的 OpenAI 聊天模型封装。
from langchain_openai import ChatOpenAI


# 定义配置缺失时抛出的专用异常。
class ConfigurationError(ValueError):
    """表示模型调用所需配置缺失。"""


# 将设置对象定义为不可变数据类。
@dataclass(frozen=True)
# 定义保存模型配置的数据结构。
class Settings:
    # 声明 API 密钥字段。
    api_key: str
    # 声明模型名称字段。
    model: str
    # 声明 OpenAI 兼容服务地址字段。
    base_url: str


# 定义读取并校验模型配置的函数。
def get_settings() -> Settings:
    """读取项目 .env 文件并返回模型配置。"""
    # 加载 langchain-learn 目录中的本地配置文件。
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    # 读取 OpenAI API 密钥。
    api_key = os.getenv("OPENAI_API_KEY")
    # 在密钥缺失时阻止模型调用。
    if not api_key:
        # 提示用户创建配置文件并填写密钥。
        raise ConfigurationError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    # 返回密钥、模型名称和服务地址组成的配置对象。
    return Settings(
        api_key=api_key,
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )


# 定义创建聊天模型实例的函数。
def get_model() -> ChatOpenAI:
    """根据环境配置创建 OpenAI 兼容聊天模型。"""
    # 获取已校验的模型配置。
    settings = get_settings()
    # 使用配置创建聊天模型实例。
    return ChatOpenAI(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
    )


# 定义将提示词和模型组合并调用的函数。
def invoke_prompt(prompt, model, values: dict[str, object]) -> str:
    """通过 LCEL 管道执行提示词并返回模型文本回复。"""
    # 将提示词和模型组合为可运行的 LCEL 链。
    chain = prompt | model
    # 传入变量执行调用并取得模型消息。
    response = chain.invoke(values)
    # 返回模型消息中的文本内容。
    return str(response.content)
