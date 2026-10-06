# 导入序列类型以接受列表或元组形式的工具与调用。
from collections.abc import Sequence
# 导入标准日志接口以记录工具执行过程。
import logging
# 导入线程池以并行执行同轮中的同步工具。
from concurrent.futures import ThreadPoolExecutor
# 导入高精度计时器以计算工具耗时。
from time import perf_counter
# 导入工具消息类型以向模型返回执行结果。
from langchain_core.messages import ToolMessage
# 导入 LangChain 工具基类以标注工具对象。
from langchain_core.tools import BaseTool

# 限制单轮工具调用的最大并发线程数。
_MAX_TOOL_WORKERS = 4
# 使用应用专用日志记录器避免 Uvicorn 访问日志格式冲突。
logger = logging.getLogger("agent.tools")

# 执行一批工具调用并按原始顺序生成对应消息。
def execute_tool_calls(tool_calls: Sequence[dict], tools: Sequence[BaseTool]) -> list[ToolMessage]:
    """并行执行工具调用，并为每个调用返回一条关联正确的 ToolMessage。"""
    # 建立工具名称到工具对象的映射。
    tools_by_name = {tool.name: tool for tool in tools}
    # 根据实际调用数和并发上限确定线程数量。
    worker_count = min(len(tool_calls), _MAX_TOOL_WORKERS)
    # 记录同轮工具调用总数及并发限制。
    logger.info("工具批次开始 call_count=%s max_workers=%s", len(tool_calls), worker_count)
    # 为所有工具调用创建并发执行池。
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        # 按模型返回顺序提交工具调用及其对应工具对象。
        futures = [
            executor.submit(_run_tool, tool_call, tools_by_name.get(tool_call["name"]))
            for tool_call in tool_calls
        ]
        # 按提交顺序取回结果，保持结果和调用 ID 的对应关系。
        observations = [future.result() for future in futures]
    # 按调用顺序将每个结果关联到对应工具调用 ID。
    tool_messages = [
        ToolMessage(content=observation, tool_call_id=tool_call["id"])
        for tool_call, observation in zip(tool_calls, observations)
    ]
    # 记录同轮工具调用全部完成。
    logger.info("工具批次完成 call_count=%s", len(tool_messages))
    # 返回按原调用顺序排列的工具消息。
    return tool_messages

# 执行单个工具调用并把工具异常转成观察文本。
def _run_tool(tool_call: dict, selected_tool: BaseTool | None) -> str:
    # 记录工具开始时间以便输出单次执行耗时。
    tool_started_at = perf_counter()
    # 读取工具名称用于日志字段。
    tool_name = tool_call.get("name", "unknown")
    # 读取模型生成的调用 ID 以关联同轮日志。
    tool_call_id = tool_call.get("id", "unknown")
    # 记录工具调用开始，不输出可能敏感的参数内容。
    logger.info("工具调用开始 name=%s tool_call_id=%s", tool_name, tool_call_id)
    # 对未提供的工具返回清楚的错误观察。
    if selected_tool is None:
        # 计算未知工具请求的处理耗时。
        elapsed_ms = (perf_counter() - tool_started_at) * 1000
        # 返回模型请求的未知工具名称。
        logger.warning("工具不存在 name=%s tool_call_id=%s duration_ms=%.2f", tool_name, tool_call_id, elapsed_ms)
        # 返回未知工具提示供模型观察。
        return f"工具不存在：{tool_name}"
    # 尝试使用工具参数调用工具。
    try:
        # 调用工具并转换结果为文本。
        result = str(selected_tool.invoke(tool_call["args"]))
        # 计算工具成功执行耗时。
        elapsed_ms = (perf_counter() - tool_started_at) * 1000
        # 记录工具成功完成及返回文本长度。
        logger.info(
            "工具调用完成 name=%s tool_call_id=%s duration_ms=%.2f result_chars=%s",
            tool_name,
            tool_call_id,
            elapsed_ms,
            len(result),
        )
        # 返回工具结果供模型下一轮推理。
        return result
    # 把工具执行错误转成模型可读取的观察结果。
    except Exception as error:
        # 计算工具失败前的执行耗时。
        elapsed_ms = (perf_counter() - tool_started_at) * 1000
        # 记录工具异常堆栈及关联调用标识。
        logger.exception(
            "工具调用失败 name=%s tool_call_id=%s duration_ms=%.2f",
            tool_name,
            tool_call_id,
            elapsed_ms,
        )
        # 返回简短错误文本，供模型决定如何继续。
        return f"工具执行失败：{error}"
