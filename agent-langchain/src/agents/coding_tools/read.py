# 导入 LangChain 工具装饰器以注册结构化工具。
from langchain_core.tools import tool
# 导入 Pydantic 基类以描述工具输入参数。
from pydantic import BaseModel, Field

# 导入共享路径校验和输出限制函数。
from agents.coding_tools.common import limit_output, resolve_workspace_path

# 定义 Read 工具的结构化输入参数。
class ReadInput(BaseModel):
    # 说明需要读取的工作区文件相对路径。
    path: str = Field(description="要读取的项目文件相对路径")
    # 说明读取范围的起始行号。
    start_line: int = Field(default=1, description="读取范围的起始行号，从 1 开始，默认是第 1 行")
    # 说明读取范围的结束行号。
    end_line: int | None = Field(default=None, description="读取范围的结束行号，包含该行；省略时读取到文件末尾")

# 声明读取工作区文本文件的 Read 工具。
@tool(args_schema=ReadInput)
# 按可选行号范围读取指定文件。
def Read(path: str, start_line: int = 1, end_line: int | None = None) -> str:
    """读取工作区文本文件；path 是文件相对路径，start_line 和 end_line 用于指定包含端点的行号范围。"""
    # 校验并解析目标文件路径。
    file_path = resolve_workspace_path(path)
    # 拒绝读取不存在或非普通文件的目标。
    if not file_path.is_file():
        # 返回目标文件无效的说明。
        return f"不是有效文件：{path}"
    # 使用 UTF-8 读取文件并处理常见文件错误。
    try:
        # 将文件内容拆分为文本行。
        lines = file_path.read_text(encoding="utf-8").splitlines()
    # 将编码或权限错误转换为工具结果。
    except (UnicodeDecodeError, OSError) as error:
        # 返回读取失败的具体原因。
        return f"读取文件失败：{error}"
    # 规范化起始行号。
    first_line = max(start_line, 1)
    # 根据结束行号计算读取范围。
    last_line = len(lines) if end_line is None else min(max(end_line, first_line), len(lines))
    # 为每行添加原始行号并限制输出长度。
    return limit_output("\n".join(f"{number}: {lines[number - 1]}" for number in range(first_line, last_line + 1)))
