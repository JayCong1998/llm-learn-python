"""FastAPI 示例使用的可覆盖依赖工厂。"""

# 导入 SQLite 标准连接库。
import sqlite3
# 导入文件系统路径类型。
from pathlib import Path

# 导入 FastAPI 依赖声明和请求类型。
from fastapi import Depends, Request
# 导入进程内 LangGraph 检查点存储。
from langgraph.checkpoint.memory import InMemorySaver
# 导入 LangChain OpenAI 聊天模型。
from langchain_openai import ChatOpenAI

# 导入顶层模型配置读取函数和异常。
from app import ConfigurationError as ModelConfigurationError
# 导入顶层模型配置读取函数。
from app import get_settings
# 导入 API 配置异常。
from api.core.errors import ConfigurationError
# 导入 API 非密钥配置和后端枚举。
from api.core.config import ApiSettings, MemoryBackend
# 导入消息记忆服务。
from api.modules.memory.service import MemoryChatService
# 导入 MCP 调用服务。
from api.modules.mcp.service import McpService
# 导入本地技能加载和调用服务。
from api.modules.skills.service import SkillLoader, SkillService
# 导入提示词调用服务。
from api.modules.prompts.service import PromptService
# 导入流式输出服务。
from api.modules.streaming.service import StreamingService
# 导入结构化输出服务。
from api.modules.structured.service import StructuredOutputService
# 导入安全本地工具服务。
from api.modules.tools.service import ToolService


# 创建统一配置的聊天模型。
def get_chat_model() -> ChatOpenAI:
    # 尝试读取既有模型环境配置。
    try:
        # 获取经过校验的模型设置。
        settings = get_settings()
    # 捕获顶层配置异常。
    except ModelConfigurationError as error:
        # 映射为 API 稳定配置异常。
        raise ConfigurationError("缺少模型调用配置") from error
    # 尝试构造配置完成的聊天模型。
    try:
        # 返回统一的 OpenAI 兼容模型适配器。
        return ChatOpenAI(
            model=settings.model,
            api_key=settings.api_key,
            base_url=settings.base_url,
        )
    # 捕获 URL 等模型适配器初始化异常。
    except Exception as error:
        # 映射为不回显密钥或地址的稳定配置错误。
        raise ConfigurationError("聊天模型初始化失败") from error


# 创建提示词调用服务。
def get_prompt_service(
    model: ChatOpenAI = Depends(get_chat_model),
) -> PromptService:
    # 注入统一聊天模型。
    return PromptService(model)


# 创建流式输出服务。
def get_streaming_service(
    model: ChatOpenAI = Depends(get_chat_model),
) -> StreamingService:
    # 注入统一聊天模型。
    return StreamingService(model)


# 创建结构化输出服务。
def get_structured_service(
    model: ChatOpenAI = Depends(get_chat_model),
) -> StructuredOutputService:
    # 注入统一聊天模型。
    return StructuredOutputService(model)


# 创建安全本地工具服务。
def get_tool_service(
    model: ChatOpenAI = Depends(get_chat_model),
) -> ToolService:
    # 注入统一聊天模型。
    return ToolService(model)


# 读取 API 运行配置。
def get_api_settings() -> ApiSettings:
    # 从环境变量创建不可变配置。
    return ApiSettings.from_environment()


# 创建本地或远程 MCP 调用服务。
def get_mcp_service(
    model: ChatOpenAI = Depends(get_chat_model),
    settings: ApiSettings = Depends(get_api_settings),
) -> McpService:
    # 注入配置和统一聊天模型。
    return McpService(settings=settings, model=model)


# 创建固定项目技能根目录加载器。
def get_skill_loader() -> SkillLoader:
    # 定位项目根目录下的技能文件夹。
    skill_root = Path(__file__).resolve().parents[2] / "skills"
    # 返回执行路径白名单校验的加载器。
    return SkillLoader(skill_root)


# 创建本地技能模型调用服务。
def get_skill_service(
    loader: SkillLoader = Depends(get_skill_loader),
) -> SkillService:
    # 注入固定加载器并延迟创建聊天模型。
    return SkillService(loader=loader, model_factory=get_chat_model)


# 获取当前 FastAPI 应用独占的消息记忆服务。
def get_memory_service(request: Request) -> MemoryChatService:
    # 读取当前应用资源状态。
    state = request.app.state
    # 直接复用已经创建的记忆服务。
    if state.memory_service is not None:
        # 返回当前应用独占实例。
        return state.memory_service
    # 使用应用级锁避免并发首次请求重复创建资源。
    with state.memory_resource_lock:
        # 在获得锁后再次检查实例。
        if state.memory_service is not None:
            # 返回其他请求已经创建的实例。
            return state.memory_service
        # 读取记忆后端配置。
        settings = get_api_settings()
        # 创建统一聊天模型。
        model = get_chat_model()
        # 默认没有需要持久关闭的数据库连接。
        connection = None
        # 为默认模式创建进程内检查点存储。
        if settings.memory_backend is MemoryBackend.MEMORY:
            # 使用适合教学的进程内 saver。
            checkpointer = InMemorySaver()
        # 为持久化模式创建 SQLite 检查点存储。
        else:
            # 创建 SQLite saver 和对应连接。
            checkpointer, connection = _create_sqlite_checkpointer(
                settings.memory_sqlite_path
            )
        # 尝试创建当前应用独占的记忆服务。
        try:
            # 保存已经成功初始化的记忆服务。
            state.memory_service = MemoryChatService(
                model=model,
                checkpointer=checkpointer,
            )
        # 在服务构造失败时释放本次新建连接。
        except Exception:
            # 仅处理 SQLite 模式创建的持久连接。
            if connection is not None:
                # 隔离连接关闭阶段的次生异常。
                try:
                    # 立即关闭未被服务接管的连接。
                    connection.close()
                # 保留原始服务构造异常。
                except Exception:
                    # 忽略无法恢复的关闭异常。
                    pass
            # 继续抛出原始稳定或内部异常。
            raise
        # 仅在服务成功后把连接交给应用生命周期。
        if connection is not None:
            # 注册 SQLite 连接关闭函数。
            state.resource_closers.append(connection.close)
        # 返回新创建的记忆服务。
        return state.memory_service


# 创建可选依赖提供的 SQLite 检查点存储。
def _create_sqlite_checkpointer(configured_path: Path):
    # 延迟导入单独安装的 SQLite checkpointer。
    try:
        # 导入 SQLite saver 实现。
        from langgraph.checkpoint.sqlite import SqliteSaver
    # 在依赖未安装时提供可操作提示。
    except ImportError as error:
        # 抛出稳定配置异常。
        raise ConfigurationError(
            "SQLite 记忆需要安装 langgraph-checkpoint-sqlite"
        ) from error
    # 将相对路径定位到项目根目录。
    database_path = (
        configured_path
        if configured_path.is_absolute()
        else Path(__file__).resolve().parents[2] / configured_path
    )
    # 创建数据库父目录。
    database_path.parent.mkdir(parents=True, exist_ok=True)
    # 创建允许 FastAPI 工作线程访问的 SQLite 连接。
    connection = sqlite3.connect(database_path, check_same_thread=False)
    # 创建线程安全锁保护的 SQLite saver。
    checkpointer = SqliteSaver(connection)
    # 返回 saver 和需要生命周期关闭的连接。
    return checkpointer, connection
