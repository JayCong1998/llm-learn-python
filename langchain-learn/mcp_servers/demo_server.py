"""通过 stdio 暴露确定性工具的内置 MCP Server。"""

# 导入 MCP SDK 的轻量服务封装。
from mcp.server.fastmcp import FastMCP

# 创建教学用 MCP 服务。
mcp = FastMCP("LangChain Demo MCP")


# 注册两数相加工具。
@mcp.tool()
def add(a: float, b: float) -> float:
    """返回两个数字的和。"""
    # 返回确定性的加法结果。
    return a + b


# 注册固定城市说明工具。
@mcp.tool()
def city_note(city: str) -> str:
    """返回教学用的固定城市说明。"""
    # 定义不依赖网络的城市数据。
    notes = {
        # 保存北京说明。
        "北京": "中国首都",
        # 保存上海说明。
        "上海": "中国重要的国际化城市",
    }
    # 返回匹配结果或明确的未知提示。
    return notes.get(city, "暂无该城市的演示数据")


# 仅在脚本直接执行时启动服务。
if __name__ == "__main__":
    # 以标准输入输出协议运行 MCP。
    mcp.run(transport="stdio")
