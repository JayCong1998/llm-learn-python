# 导入文件模式匹配和正则表达式模块。
import fnmatch
import re

# 导入 LangChain 工具装饰器以注册结构化工具。
from langchain_core.tools import tool
# 导入 Pydantic 基类以描述工具输入参数。
from pydantic import BaseModel, Field

# 导入共享输出限制和路径校验函数。
from agents.coding_tools.common import limit_output, resolve_workspace_path

# 定义 Grep 工具的结构化输入参数。
class GrepInput(BaseModel):
    # 说明用于搜索文件内容的正则表达式。
    pattern: str = Field(description="用于匹配文件内容行的正则表达式")
    # 说明限定搜索范围的工作区相对路径。
    path: str = Field(default=".", description="要搜索的工作区相对目录或文件路径，默认是项目根目录")
    # 说明用于过滤候选文件名的 glob 模式。
    glob: str = Field(default="*", description="候选文件名过滤模式，默认匹配所有文件")

# 声明正则搜索文件内容的 Grep 工具。
@tool(args_schema=GrepInput)
# 查找工作区文本文件中的匹配行。
def Grep(pattern: str, path: str = ".", glob: str = "*") -> str:
    """按正则表达式搜索工作区文件；pattern 是正则，path 是搜索路径，glob 按文件名过滤。"""
    # 将搜索起点约束在工作区范围内。
    search_root = resolve_workspace_path(path)
    # 拒绝不存在的搜索位置。
    if not search_root.is_dir() and not search_root.is_file():
        # 返回搜索路径无效的说明。
        return f"路径不存在：{path}"
    # 编译用户提供的正则表达式。
    try:
        # 创建用于逐行匹配的正则对象。
        expression = re.compile(pattern)
    # 捕获无效表达式并给出说明。
    except re.error as error:
        # 返回正则语法错误信息。
        return f"正则表达式无效：{error}"
    # 对单文件路径直接搜索该文件。
    candidates = [search_root] if search_root.is_file() else search_root.rglob("*")
    # 初始化搜索结果集合。
    matches = []
    # 逐个处理候选文件。
    for file_path in candidates:
        # 跳过目录及文件名不匹配的条目。
        if not file_path.is_file() or not fnmatch.fnmatch(file_path.name, glob):
            # 继续处理下一个候选文件。
            continue
        # 跳过版本控制、依赖和缓存目录。
        if any(part in {".git", ".venv", "venv", "node_modules", "__pycache__"} for part in file_path.relative_to(resolve_workspace_path(".")).parts):
            # 继续处理下一个候选文件。
            continue
        # 尝试以 UTF-8 文本读取候选文件。
        try:
            # 按行号查找匹配内容。
            for line_number, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), 1):
                # 为匹配项添加文件路径和行号。
                if expression.search(line):
                    # 保存一条带定位信息的结果。
                    matches.append(f"{file_path.relative_to(resolve_workspace_path('.'))}:{line_number}:{line}")
                # 达到搜索结果上限时停止当前文件扫描。
                if len(matches) >= 1_000:
                    # 结束当前文件的行遍历。
                    break
        # 忽略无法作为 UTF-8 文本读取的文件。
        except (UnicodeDecodeError, OSError):
            # 继续处理后续候选文件。
            continue
        # 达到搜索结果上限时停止遍历文件。
        if len(matches) >= 1_000:
            # 结束候选文件遍历。
            break
    # 返回匹配内容并限制总输出长度。
    return limit_output("\n".join(matches) or "没有匹配内容。")
