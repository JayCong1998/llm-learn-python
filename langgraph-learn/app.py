"""Minimal LangGraph workflow with a single model node."""

# 导入不可变数据类装饰器。
from dataclasses import dataclass
# 导入读取环境变量的标准库。
import os
# 导入用于定位项目配置文件的路径工具。
from pathlib import Path
# 导入声明图状态字段的类型工具。
from typing import TypedDict

# 导入加载 dotenv 配置文件的函数。
from dotenv import load_dotenv
# 导入 LangChain 的 OpenAI 聊天模型封装。
from langchain_openai import ChatOpenAI
# 导入 LangGraph 的图边界常量和图构建器。
from langgraph.graph import END, START, StateGraph


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


# 定义图工作流中传递的数据结构。
class GraphState(TypedDict):
    # 声明传入模型的问题字段。
    question: str
    # 声明由模型节点写入的回答字段。
    answer: str


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
    # 返回密钥和模型名称组成的配置对象。
    return Settings(api_key=api_key, model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))


# 定义构建最小 LangGraph 工作流的函数。
def build_graph():
    """Build START -> call_model -> END for the configured chat model."""
    # 获取已经校验过的模型配置。
    settings = get_settings()
    # 使用配置创建 LangChain 聊天模型实例。
    model = ChatOpenAI(model=settings.model, api_key=settings.api_key)

    # 定义负责调用模型的图节点。
    def call_model(state: GraphState) -> dict[str, str]:
        # 将问题交给模型并把回答写入图状态。
        return {"answer": str(model.invoke(state["question"]).content)}

    # 使用声明的状态类型创建工作流构建器。
    workflow = StateGraph(GraphState)
    # 注册模型调用节点。
    workflow.add_node("call_model", call_model)
    # 连接图起点到模型调用节点。
    workflow.add_edge(START, "call_model")
    # 连接模型调用节点到图终点。
    workflow.add_edge("call_model", END)
    # 编译并返回可调用的工作流。
    return workflow.compile()
