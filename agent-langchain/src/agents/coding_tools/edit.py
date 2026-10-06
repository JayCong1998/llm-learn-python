# 导入 LangChain 工具装饰器以注册结构化工具。
from langchain_core.tools import tool
# 导入 Pydantic 基类以描述工具输入参数。
from pydantic import BaseModel, Field

# 导入共享路径校验函数。
from agents.coding_tools.common import resolve_workspace_path

# 定义 Edit 工具的结构化输入参数。
class EditInput(BaseModel):
    # 说明目标文件在项目工作区中的相对路径。
    path: str = Field(description="要修改的项目文件相对路径")
    # 说明需要在文件中唯一匹配的原始文本。
    old_text: str = Field(description="需要被替换且必须唯一匹配的原始文本")
    # 说明用于替换原始文本的新文本。
    new_text: str = Field(description="替换原始文本的新内容")

# 声明按文本片段修改文件的 Edit 工具。
@tool(args_schema=EditInput)
# 只在旧文本唯一匹配时写入替换结果。
def Edit(path: str, old_text: str, new_text: str) -> str:
    """在工作区文件中精确替换文本；path 是文件相对路径，old_text 必须唯一，new_text 是替换内容。"""
    # 校验并解析目标文件路径。
    file_path = resolve_workspace_path(path)
    # 拒绝修改不存在或非普通文件的目标。
    if not file_path.is_file():
        # 返回目标文件无效的说明。
        return f"不是有效文件：{path}"
    # 尝试按 UTF-8 读取文件并保留换行符。
    try:
        # 读取原始文本内容以进行精确匹配。
        with file_path.open("r", encoding="utf-8", newline="") as file:
            # 将全部文件文本载入内存。
            content = file.read()
    # 将读取失败转换为工具结果。
    except (UnicodeDecodeError, OSError) as error:
        # 返回读取失败的原因。
        return f"读取文件失败：{error}"
    # 统计旧文本的出现次数。
    match_count = content.count(old_text) if old_text else 0
    # 拒绝没有匹配或匹配多处的替换请求。
    if match_count != 1:
        # 返回匹配次数以便调用方缩小文本上下文。
        return f"替换未执行：old_text 必须恰好匹配一次，实际匹配 {match_count} 次。"
    # 只替换唯一匹配位置。
    updated_content = content.replace(old_text, new_text, 1)
    # 按原换行文本模式写回修改结果。
    with file_path.open("w", encoding="utf-8", newline="") as file:
        # 写入完成替换后的全文。
        file.write(updated_content)
    # 返回成功更新的相对路径。
    return f"已更新 {file_path.relative_to(resolve_workspace_path('.'))}。"
