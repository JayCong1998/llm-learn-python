# 导入日期时间类型以生成当前时间。
from datetime import datetime
# 导入时区工具以解析用户指定的时区。
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
# 导入 LangChain 工具装饰器以注册可调用工具。
from langchain_core.tools import tool

# 定义少量模拟天气数据，供示例查询使用。
_WEATHER_DATA = {
    "北京": {"天气": "晴", "温度": 22, "湿度": 35, "风力": "微风"},
    "上海": {"天气": "多云", "温度": 25, "湿度": 68, "风力": "东风 2 级"},
    "广州": {"天气": "小雨", "温度": 28, "湿度": 82, "风力": "南风 3 级"},
    "深圳": {"天气": "晴转多云", "温度": 29, "湿度": 75, "风力": "东南风 2 级"},
    "杭州": {"天气": "阴", "温度": 24, "湿度": 70, "风力": "东北风 2 级"},
}

# 声明查询当前时间的 LangChain 工具。
@tool
# 根据用户提供的时区返回当前本地时间。
def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """查询指定时区的当前日期和时间。timezone 使用 IANA 时区名，例如 Asia/Shanghai；默认 Asia/Shanghai。"""
    # 尝试按指定时区格式化当前时间。
    try:
        current_time = datetime.now(ZoneInfo(timezone))
    # 对无效时区名称返回可读错误提示。
    except ZoneInfoNotFoundError:
        # 告知用户无效时区并给出正确示例。
        return f"无法识别时区“{timezone}”，请使用 IANA 时区名，例如 Asia/Shanghai。"
    # 返回含时区名称的本地日期与时间。
    return current_time.strftime(f"%Y-%m-%d %H:%M:%S %Z（{timezone}）")

# 声明模拟天气查询的 LangChain 工具。
@tool
# 按城市名称查询预置的模拟天气信息。
def get_weather(city: str) -> str:
    """查询指定城市的模拟天气。city 是城市名称；当前支持北京、上海、广州、深圳和杭州。"""
    # 清理城市名两侧空白后查找模拟天气数据。
    weather = _WEATHER_DATA.get(city.strip())
    # 对未收录城市返回支持范围。
    if weather is None:
        # 返回当前可查询城市列表。
        return f"暂不支持查询“{city}”，目前支持的城市有：{'、'.join(_WEATHER_DATA)}。"
    # 拼接天气、温度、湿度和风力信息。
    return (
        f"{city.strip()}的模拟天气：{weather['天气']}，"
        f"气温 {weather['温度']}°C，湿度 {weather['湿度']}%，风力{weather['风力']}。"
    )

# 汇总可供 Agent 绑定的工具。
weather_time_tools = [get_current_time, get_weather]
