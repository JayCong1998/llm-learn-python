# 导入环境变量读取工具。
import os
# 导入日期时间处理工具。
from datetime import datetime
# 导入文件路径类型。
from pathlib import Path
# 导入时区处理工具。
from zoneinfo import ZoneInfo

# 导入 .env 文件加载函数。
from dotenv import load_dotenv
# 导入 FastAPI 路由与查询参数声明工具。
from fastapi import APIRouter, Query
# 导入异步 HTTP 客户端。
import httpx
# 导入 LangChain 人类与工具消息类型。
from langchain_core.messages import HumanMessage, ToolMessage
# 导入 LangChain 工具装饰器。
from langchain_core.tools import tool
# 导入 OpenAI 的 LangChain 聊天模型实现。
from langchain_openai import ChatOpenAI

# 创建工具 Agent 路由实例。
router = APIRouter(tags=["tool-agent"])


# 加载项目根目录中的 .env 文件。
def load_environment(env_file: Path | None = None) -> None:
    # 确定演示目录父级中的默认 .env 路径。
    dotenv_path = env_file or Path(__file__).parents[1] / ".env"
    # 加载配置且保留系统中已存在的同名变量。
    load_dotenv(dotenv_path=dotenv_path, override=False)


# 在创建模型前加载环境变量。
load_environment()


# 创建配置完成的 MiniMax 聊天模型。
def get_llm() -> ChatOpenAI:
    # 读取 MiniMax API 密钥。
    api_key = os.getenv("MINIMAX_API_KEY")
    # 在未配置密钥时阻止应用发送无效请求。
    if not api_key:
        # 提示调用方配置必需的 MiniMax 密钥。
        raise RuntimeError("请设置 MINIMAX_API_KEY 环境变量。")
    # 读取 MiniMax 模型名称并提供默认值。
    model_name = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")
    # 读取中国大陆的 OpenAI 兼容 API 端点。
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
    # 返回支持工具调用的聊天模型。
    return ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url, temperature=0)


# 定义 Open-Meteo 天气代码的中文描述。
WEATHER_DESCRIPTIONS = {0: "晴", 1: "大部晴朗", 2: "局部多云", 3: "阴", 45: "雾", 61: "小雨", 63: "中雨", 65: "大雨", 71: "小雪", 73: "中雪", 75: "大雪", 80: "小阵雨", 81: "中阵雨", 82: "强阵雨", 95: "雷暴"}


# 查询中国标准时间。
@tool
def get_current_time() -> str:
    """查询当前中国标准时间。"""
    # 获取上海时区的当前时间。
    current_time = datetime.now(ZoneInfo("Asia/Shanghai"))
    # 返回便于语言模型使用的格式化时间。
    return current_time.strftime("当前中国标准时间：%Y-%m-%d %H:%M:%S %Z")


# 根据城市名称请求当前天气。
async def fetch_weather(city: str) -> str:
    # 创建带超时控制的异步 HTTP 客户端。
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 请求城市名称对应的地理坐标。
        location_response = await client.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1, "language": "zh", "format": "json"})
        # 在地理编码请求失败时抛出异常。
        location_response.raise_for_status()
        # 获取第一个匹配城市列表。
        locations = location_response.json().get("results", [])
        # 在找不到城市时返回可读提示。
        if not locations:
            # 告知语言模型未找到城市。
            return f"未找到城市“{city}”，请提供更具体的城市名称。"
        # 读取首个匹配城市的信息。
        location = locations[0]
        # 请求该城市的当前天气指标。
        weather_response = await client.get("https://api.open-meteo.com/v1/forecast", params={"latitude": location["latitude"], "longitude": location["longitude"], "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m", "timezone": "auto"})
        # 在天气请求失败时抛出异常。
        weather_response.raise_for_status()
        # 解析当前天气响应数据。
        weather_data = weather_response.json()
    # 读取当前天气指标。
    current = weather_data["current"]
    # 将天气代码转为中文描述。
    description = WEATHER_DESCRIPTIONS.get(current["weather_code"], "未知天气")
    # 返回包含城市和核心气象指标的文本。
    return f"{location['name']}当前天气：{description}，气温 {current['temperature_2m']}°C，体感 {current['apparent_temperature']}°C，相对湿度 {current['relative_humidity_2m']}%，风速 {current['wind_speed_10m']} km/h。"


# 根据城市名称查询当前天气。
@tool
async def get_weather(city: str) -> str:
    """查询指定城市的当前天气，city 应为城市名称，例如“北京”或“Shanghai”。"""
    # 尝试请求城市的当前天气。
    try:
        # 调用内部天气请求函数。
        return await fetch_weather(city)
    # 捕获网络连接和 HTTP 状态异常。
    except httpx.HTTPError:
        # 返回可供语言模型解释的友好错误。
        return "天气查询暂时不可用，请稍后重试。"


# 收集可供语言模型调用的工具。
AVAILABLE_TOOLS = [get_current_time, get_weather]
# 建立工具名称到工具实例的映射。
TOOLS_BY_NAME = {tool_item.name: tool_item for tool_item in AVAILABLE_TOOLS}


# 使用支持工具调用的语言模型回答用户问题。
async def run_tool_agent(message: str) -> str:
    # 获取已配置的聊天模型。
    llm = get_llm()
    # 为模型绑定可调用工具定义。
    llm_with_tools = llm.bind_tools(AVAILABLE_TOOLS)
    # 创建包含用户问题的初始消息列表。
    messages = [HumanMessage(content=message)]
    # 最多执行三轮工具调用以避免模型无限循环。
    for _ in range(3):
        # 请求模型生成回答或工具调用。
        response = await llm_with_tools.ainvoke(messages)
        # 在模型无需工具时返回最终文本。
        if not response.tool_calls:
            # 返回模型的文本回答。
            return str(response.content)
        # 将模型的工具调用消息加入对话。
        messages.append(response)
        # 执行模型请求的每一个工具调用。
        for tool_call in response.tool_calls:
            # 根据工具名称取得工具实例。
            selected_tool = TOOLS_BY_NAME.get(tool_call["name"])
            # 在工具名称无效时构造错误结果。
            if selected_tool is None:
                # 返回工具不可用的说明。
                tool_result = f"工具 {tool_call['name']} 不可用。"
            else:
                # 异步执行工具并传入模型提供的参数。
                tool_result = await selected_tool.ainvoke(tool_call["args"])
            # 将工具执行结果回传给模型。
            messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))
    # 返回工具调用轮数达到上限的提示。
    return "工具调用次数达到上限，请换一种方式提问。"


# 提供由 LLM 调用时间和天气工具的 Agent 接口。
@router.get("/agent/chat")
async def agent_chat(message: str = Query(min_length=1, description="发送给 Agent 的文本")) -> dict[str, str]:
    # 获取语言模型结合工具后的最终回答。
    content = await run_tool_agent(message)
    # 返回 Agent 的文本结果。
    return {"content": content}
