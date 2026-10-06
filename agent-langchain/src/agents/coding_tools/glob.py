# 导入路径匹配所需的标准库模块。
import fnmatch
from pathlib import Path

# 导入 LangChain 工具装饰器以注册结构化工具。
from langchain_core.tools import tool

# 导入共享工作区路径校验函数。
from agents.coding_tools.common import resolve_workspace_path

# 声明按路径模式搜索文件的 Glob 工具。
@tool
# 返回工作区内匹配 glob 模式的路径。
def Glob(pattern: str, path: str = ".") -> str:
    """按模式查找项目文件。pattern 是文件名或相对路径模式（例如 src/**/*.py）；path 是搜索起点，默认为项目根目录。"""
    # 将搜索起点约束在工作区目录内。
    search_root = resolve_workspace_path(path)
    # 对无效搜索目录返回说明。
    if not search_root.is_dir():
        # 告知调用方搜索起点不是目录。
        return f"不是有效目录：{path}"
    # 按 glob 语义遍历并筛选工作区路径。
    matches = [
        item.relative_to(resolve_workspace_path(".")).as_posix()
        for item in search_root.rglob("*")
        if fnmatch.fnmatch(item.relative_to(search_root).as_posix(), pattern)
        or Path(item.relative_to(search_root).as_posix()).match(pattern)
    ]
    # 排序并限制结果数量。
    return "\n".join(sorted(matches)[:2_000]) or "没有匹配的路径。"
