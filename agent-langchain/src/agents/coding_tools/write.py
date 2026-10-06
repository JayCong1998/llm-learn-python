# 导入 LangChain 工具装饰器以注册结构化工具。
from langchain_core.tools import tool

# 导入共享路径校验函数。
from agents.coding_tools.common import resolve_workspace_path

# 声明创建或整体写入文件的 Write 工具。
@tool
# 将给定内容完整写入工作区文件。
def Write(path: str, content: str) -> str:
    """创建或完整覆盖工作区文件。path 是文件相对路径；content 是要写入的完整文本内容。"""
    # 校验并解析目标文件路径。
    file_path = resolve_workspace_path(path)
    # 自动创建目标文件所需的父目录。
    file_path.parent.mkdir(parents=True, exist_ok=True)
    # 使用 UTF-8 编码写入文件内容。
    file_path.write_text(content, encoding="utf-8")
    # 返回写入文件的路径和字符数。
    return f"已写入 {file_path.relative_to(resolve_workspace_path('.'))}（{len(content)} 个字符）。"
