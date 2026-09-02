"""FastAPI 示例使用的非密钥运行配置。"""

# 导入不可变数据类装饰器。
from dataclasses import dataclass
# 导入字符串枚举基类。
from enum import Enum
# 导入 JSON 解析工具。
import json
# 导入环境变量读取工具。
import os
# 导入文件系统路径类型。
from pathlib import Path

# 导入安全配置异常。
from api.core.errors import ConfigurationError


# 定义可选的消息记忆后端。
class MemoryBackend(str, Enum):
    # 声明进程内记忆模式。
    MEMORY = "memory"
    # 声明 SQLite 持久化模式。
    SQLITE = "sqlite"


# 定义可选的 MCP 连接模式。
class McpMode(str, Enum):
    # 声明内置 stdio MCP 模式。
    LOCAL = "local"
    # 声明远程 HTTP MCP 模式。
    REMOTE = "remote"


# 将 API 设置定义为不可变对象。
@dataclass(frozen=True)
class ApiSettings:
    # 保存消息记忆后端。
    memory_backend: MemoryBackend
    # 保存 SQLite 文件路径。
    memory_sqlite_path: Path
    # 保存 MCP 连接模式。
    mcp_mode: McpMode
    # 保存可选远程 MCP 地址。
    mcp_remote_url: str | None
    # 保存远程 MCP 请求头。
    mcp_remote_headers: dict[str, str]

    # 从环境变量创建 API 配置。
    @classmethod
    def from_environment(cls) -> "ApiSettings":
        # 解析消息记忆后端枚举。
        memory_backend = _parse_enum(
            MemoryBackend,
            os.getenv("MEMORY_BACKEND", MemoryBackend.MEMORY.value),
            "MEMORY_BACKEND",
        )
        # 解析 MCP 连接模式枚举。
        mcp_mode = _parse_enum(
            McpMode,
            os.getenv("MCP_MODE", McpMode.LOCAL.value),
            "MCP_MODE",
        )
        # 解析远程 MCP 请求头。
        headers = _parse_headers(os.getenv("MCP_REMOTE_HEADERS", "{}"))
        # 返回完整的不可变配置。
        return cls(
            memory_backend=memory_backend,
            memory_sqlite_path=Path(
                os.getenv("MEMORY_SQLITE_PATH", "data/memory.sqlite")
            ),
            mcp_mode=mcp_mode,
            mcp_remote_url=os.getenv("MCP_REMOTE_URL"),
            mcp_remote_headers=headers,
        )


# 将字符串解析为指定枚举成员。
def _parse_enum(enum_type, value: str, variable_name: str):
    # 尝试匹配枚举值。
    try:
        # 返回匹配到的枚举成员。
        return enum_type(value)
    # 捕获不支持的枚举值。
    except ValueError as error:
        # 抛出不回显原始值的安全错误。
        raise ConfigurationError(f"{variable_name} 配置无效") from error


# 解析并校验远程 MCP 请求头。
def _parse_headers(raw_headers: str) -> dict[str, str]:
    # 尝试解析 JSON 文本。
    try:
        # 读取 JSON 对象。
        parsed = json.loads(raw_headers)
    # 捕获 JSON 语法错误。
    except json.JSONDecodeError as error:
        # 抛出不包含原始文本的安全错误。
        raise ConfigurationError("MCP_REMOTE_HEADERS 必须是 JSON 对象") from error
    # 确认顶层值为对象且所有键值均为字符串。
    if not isinstance(parsed, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in parsed.items()
    ):
        # 拒绝无法安全作为 HTTP 请求头的数据。
        raise ConfigurationError("MCP_REMOTE_HEADERS 必须只包含字符串键值")
    # 返回经过类型校验的请求头副本。
    return dict(parsed)
