# 导入类型定义以约束 Agent 工具参数。
# 导入迭代器类型以声明流式答复的返回类型。
from collections.abc import Iterator, Sequence
# 导入标准日志接口以记录 Agent 执行过程。
import logging
# 导入系统环境变量读取模块。
import os
# 导入高精度计时器以计算模型调用耗时。
from time import perf_counter, sleep
# 导入环境变量读取函数。
from dotenv import load_dotenv
# 导入 LangChain 消息类型以维护 ReAct 对话历史。
from langchain_core.messages import HumanMessage, SystemMessage
# 导入 LangChain 工具基类以描述可传入的工具。
from langchain_core.tools import BaseTool
# 导入兼容 OpenAI API 的聊天模型。
from langchain_openai import ChatOpenAI
# 导入工具执行函数以处理模型提出的工具调用。
from agents.tool_executor import execute_tool_calls
# 导入流式事件类型和统一事件模型。
from agents.stream_event import AgentStreamEvent, AgentStreamEventType

# 使用应用专用日志记录器避免 Uvicorn 访问日志格式冲突。
logger = logging.getLogger("agent.react")

# 从 .env 文件加载模型配置。
load_dotenv(override=True)

# 读取 DashScope API 密钥。
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
# 读取 Qwen 兼容接口地址。
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")
# 读取 Qwen 模型名称。
QWEN_MODEL = os.getenv("QWEN_MODEL")

# 定义使用手写 ReAct 循环的 Agent 类。
class ReactAgent:
    """根据传入工具执行模型推理、工具调用和结果观察循环。"""

    # 初始化本次 Agent 使用的模型、工具和循环上限。
    def __init__(self, tools: Sequence[BaseTool] = (), max_iterations: int = 5):
        # 创建本次 Agent 独立的聊天模型实例。
        self.model = ChatOpenAI(
            model=QWEN_MODEL,
            api_key=DASHSCOPE_API_KEY,
            base_url=QWEN_BASE_URL,
        )
        # 保存调用方指定的工具列表。
        self.tools = list(tools)
        # 保存单次请求允许的最大推理轮数。
        self.max_iterations = max_iterations

    # 定义同步执行 ReAct 循环并返回最终文本答复。
    def invoke(self, query: str) -> str:
        """处理一个用户问题并返回 Agent 的最终答复。"""
        # 将工具描述加入系统提示，引导模型按需调用工具。
        tool_descriptions = "\n".join(
            f"- {tool.name}: {tool.description}" for tool in self.tools
        )
        # 初始化要求模型在需要时使用原生工具调用的系统消息。
        system_message = SystemMessage(
            content=(
                "你是一个使用 ReAct 方法解决问题的助手。需要外部信息时调用可用工具，"
                "根据工具结果继续推理，最后用中文清晰回答。"
                f"\n可用工具：\n{tool_descriptions or '无'}"
            )
        )
        # 初始化本轮会话的消息历史。
        messages = [system_message, HumanMessage(content=query)]
        # 记录本次 Agent 执行的工具和迭代配置。
        logger.info("ReAct 开始 tool_count=%s max_iterations=%s", len(self.tools), self.max_iterations)
        # 按配置的最大轮数重复调用模型并处理工具请求。
        for iteration in range(1, self.max_iterations + 1):
            # 记录当前推理轮次开始。
            logger.info("ReAct 模型调用开始 iteration=%s", iteration)
            # 记录模型调用起始时间以计算耗时。
            model_started_at = perf_counter()
            # 绑定本 Agent 的工具定义并请求模型生成下一步。
            try:
                # 发起支持当前工具集的模型调用。
                response = self.model.bind_tools(self.tools).invoke(messages)
            # 记录模型请求失败并保留原异常供上层处理。
            except Exception:
                # 输出模型调用失败堆栈以便排查。
                logger.exception("ReAct 模型调用失败 iteration=%s", iteration)
                # 继续向调用方抛出模型异常。
                raise
            # 计算当前模型调用耗时。
            model_elapsed_ms = (perf_counter() - model_started_at) * 1000
            # 记录模型调用完成及工具请求数量。
            logger.info(
                "ReAct 模型调用完成 iteration=%s tool_call_count=%s duration_ms=%.2f",
                iteration,
                len(response.tool_calls),
                model_elapsed_ms,
            )
            # 将模型回复加入历史以保留其推理和工具调用信息。
            messages.append(response)
            # 当模型没有工具调用时，将其内容作为最终答复返回。
            if not response.tool_calls:
                # 记录 Agent 正常结束的轮次。
                logger.info("ReAct 完成 iteration=%s reason=final_answer", iteration)
                # 兼容模型返回字符串或多段内容的情况。
                return response.content if isinstance(response.content, str) else str(response.content)
            # 输出本轮模型请求的工具名称列表。
            logger.info(
                "ReAct 工具调用计划 iteration=%s tools=%s",
                iteration,
                [tool_call["name"] for tool_call in response.tool_calls],
            )
            # 执行工具调用并将对应观察消息添加到对话历史。
            messages.extend(execute_tool_calls(response.tool_calls, self.tools))
        # 记录推理轮数耗尽并准备总结阶段。
        logger.warning("ReAct 达到最大迭代次数 max_iterations=%s，开始总结", self.max_iterations)
        # 构造要求模型依据已有历史总结且禁止使用工具的提示。
        summary_instruction = HumanMessage(
            content=(
                "工具推理轮数已达到上限。请只根据当前对话历史和已有工具结果，"
                "直接用中文整理并回答用户问题；不得调用工具，也不得要求继续查询。"
                "如果现有信息不足，请明确说明限制，并给出目前能够确定的结论。"
            )
        )
        # 在完整消息历史后追加总结约束并执行最后一次模型调用。
        try:
            # 不绑定工具，要求模型只根据当前上下文生成总结。
            summary = self.model.invoke([*messages, summary_instruction])
        # 记录总结请求失败并继续向上抛出异常。
        except Exception:
            # 输出总结模型调用异常堆栈。
            logger.exception("ReAct 达到迭代上限后的总结调用失败")
            # 继续向调用方抛出总结异常。
            raise
        # 记录总结调用正常完成。
        logger.info("ReAct 总结完成")
        # 返回总结调用的文本内容。
        return summary.content if isinstance(summary.content, str) else str(summary.content)

    # 定义流式执行 ReAct 循环并逐段返回最终答复。
    def stream(self, query: str) -> Iterator[AgentStreamEvent]:
        """处理一个用户问题并产出结构化 Agent 事件。"""
        # 将工具描述加入系统提示，引导模型按需调用工具。
        tool_descriptions = "\n".join(
            f"- {tool.name}: {tool.description}" for tool in self.tools
        )
        # 初始化要求模型按需使用原生工具调用的系统消息。
        system_message = SystemMessage(
            content=(
                "你是一个使用 ReAct 方法解决问题的助手。需要外部信息时调用可用工具，"
                "根据工具结果继续推理，最后用中文清晰回答。"
                f"\n可用工具：\n{tool_descriptions or '无'}"
            )
        )
        # 初始化本轮会话的消息历史。
        messages = [system_message, HumanMessage(content=query)]
        # 发出本次 Agent 执行开始事件。
        yield AgentStreamEvent(type=AgentStreamEventType.RUN_STARTED)
        # 记录本次 Agent 执行的工具和迭代配置。
        logger.info("ReAct 流式开始 tool_count=%s max_iterations=%s", len(self.tools), self.max_iterations)
        # 按配置的最大轮数重复流式调用模型并处理工具请求。
        for iteration in range(1, self.max_iterations + 1):
            # 记录当前推理轮次开始。
            logger.info("ReAct 流式模型调用开始 iteration=%s", iteration)
            # 记录模型调用起始时间以计算耗时。
            model_started_at = perf_counter()
            # 初始化本轮模型消息以合并流式响应分块。
            response = None
            # 记录本轮已输出的文本以区分工具推理和最终答复。
            emitted_content = False
            # 绑定本 Agent 的工具定义并请求模型流式生成下一步。
            try:
                # 接收模型逐段生成的消息分块。
                for chunk in self.model.bind_tools(self.tools).stream(messages):
                    # 累加分块以还原完整消息及工具调用参数。
                    response = chunk if response is None else response + chunk
                    # 提取当前分块中的文本内容。
                    chunk_content = chunk.content
                    # 仅向调用方产出非空文本分块。
                    if isinstance(chunk_content, str) and chunk_content:
                        # 标记本轮已产出文本内容。
                        emitted_content = True
                        # 将文本分块立即交给调用方。
                        # 发出面向用户的增量文本事件。
                        yield AgentStreamEvent(type=AgentStreamEventType.CONTENT_DELTA, data=chunk_content, step=iteration)
                    # 提取模型可能提供的独立思考内容。
                    reasoning_content = getattr(chunk, "additional_kwargs", {}).get("reasoning_content")
                    # 仅当模型返回思考字段时发出思考增量事件。
                    if reasoning_content:
                        # 发出模型提供的思考内容片段。
                        yield AgentStreamEvent(type=AgentStreamEventType.THINKING_DELTA, data=reasoning_content, step=iteration)
            # 记录模型请求失败并保留原异常供上层处理。
            except Exception as error:
                # 输出模型调用失败堆栈以便排查。
                logger.exception("ReAct 流式模型调用失败 iteration=%s", iteration)
                # 发出模型调用失败事件。
                yield AgentStreamEvent(type=AgentStreamEventType.ERROR, data=str(error))
                # 继续向调用方抛出模型异常。
                raise
            # 计算当前模型调用耗时。
            model_elapsed_ms = (perf_counter() - model_started_at) * 1000
            # 兼容未产生任何消息分块的模型响应。
            if response is None:
                # 记录空响应并结束本轮流式处理。
                logger.info("ReAct 流式模型无响应 iteration=%s", iteration)
                # 结束生成器且不产出额外内容。
                # 发出无响应时的完成事件并结束生成器。
                yield AgentStreamEvent(type=AgentStreamEventType.RUN_COMPLETED, metadata={"reason": "empty_response"})
                return
            # 获取合并后的工具调用列表，兼容模型响应未提供该字段。
            tool_calls = getattr(response, "tool_calls", []) or []
            # 记录模型调用完成及工具请求数量。
            logger.info(
                "ReAct 流式模型调用完成 iteration=%s tool_call_count=%s duration_ms=%.2f",
                iteration,
                len(tool_calls),
                model_elapsed_ms,
            )
            # 将模型回复加入历史以保留其推理和工具调用信息。
            messages.append(response)
            # 当模型没有工具调用时，最终文本已在流式过程中产出。
            if not tool_calls:
                # 记录 Agent 正常结束的轮次。
                logger.info("ReAct 流式完成 iteration=%s reason=final_answer", iteration)
                # 对非字符串内容执行兼容处理并补充产出。
                if not emitted_content and response.content:
                    # 将非字符串或未从分块取得的最终内容转换为文本。
                    # 发出未从分块中取得的最终文本内容。
                    yield AgentStreamEvent(type=AgentStreamEventType.CONTENT_DELTA, data=response.content if isinstance(response.content, str) else str(response.content), step=iteration)
                # 发出本次 Agent 执行完成事件。
                yield AgentStreamEvent(type=AgentStreamEventType.RUN_COMPLETED, step=iteration)
                # 结束最终答复生成。
                return
            # 输出本轮模型请求的工具名称列表。
            logger.info(
                "ReAct 流式工具调用计划 iteration=%s tools=%s",
                iteration,
                [tool_call["name"] for tool_call in tool_calls],
            )
            # 按模型给出的调用顺序发出工具开始事件。
            for tool_call in tool_calls:
                # 发出工具调用开始事件及其参数。
                yield AgentStreamEvent(type=AgentStreamEventType.TOOL_CALL_STARTED, data=tool_call.get("args", {}), tool_name=tool_call.get("name"), tool_call_id=tool_call.get("id"), step=iteration)
            # 执行工具调用并取得对应观察消息。
            tool_messages = execute_tool_calls(tool_calls, self.tools)
            # 逐条发出工具结果事件。
            for tool_call, tool_message in zip(tool_calls, tool_messages):
                # 判断工具结果是否包含执行错误。
                result_type = AgentStreamEventType.TOOL_CALL_FAILED if str(tool_message.content).startswith(("工具执行失败：", "工具不存在：")) else AgentStreamEventType.TOOL_RESULT
                # 发出工具执行结果和调用关联信息。
                yield AgentStreamEvent(type=result_type, data=tool_message.content, tool_name=tool_call.get("name"), tool_call_id=tool_call.get("id"), step=iteration)
            # 将工具观察结果追加到对话历史供下一轮模型使用。
            messages.extend(tool_messages)



        # 记录推理轮数耗尽并准备总结阶段。
        logger.warning("ReAct 流式达到最大迭代次数 max_iterations=%s，开始总结", self.max_iterations)
        # 构造要求模型依据已有历史总结且禁止使用工具的提示。
        summary_instruction = HumanMessage(
            content=(
                "工具推理轮数已达到上限。请只根据当前对话历史和已有工具结果，"
                "直接用中文整理并回答用户问题；不得调用工具，也不得要求继续查询。"
                "如果现有信息不足，请明确说明限制，并给出目前能够确定的结论。"
            )
        )
        # 流式请求最后一次总结答复并记录异常。
        try:
            # 逐段接收总结模型产生的内容。
            for chunk in self.model.stream([*messages, summary_instruction]):
                # 提取总结分块中的文本内容。
                chunk_content = chunk.content
                # 仅向调用方产出非空文本分块。
                if isinstance(chunk_content, str) and chunk_content:
                    # 将总结文本分块立即交给调用方。
                    # 发出总结答复的增量文本事件。
                    yield AgentStreamEvent(type=AgentStreamEventType.CONTENT_DELTA, data=chunk_content, step=self.max_iterations + 1)
        # 记录总结请求失败并继续向上抛出异常。
        except Exception as error:
            # 输出总结模型调用异常堆栈。
            logger.exception("ReAct 流式达到迭代上限后的总结调用失败")
            # 继续向调用方抛出总结异常。
            # 发出总结模型调用失败事件。
            yield AgentStreamEvent(type=AgentStreamEventType.ERROR, data=str(error))
            # 继续向调用方抛出总结异常。
            raise
        # 记录总结调用正常完成。
        logger.info("ReAct 流式总结完成")
        # 发出总结阶段完成事件。
        yield AgentStreamEvent(type=AgentStreamEventType.RUN_COMPLETED, step=self.max_iterations + 1)

# 定义创建 ReAct Agent 实例的工厂函数。
def create_react_agent(tools: Sequence[BaseTool] = (), max_iterations: int = 5) -> ReactAgent:
    """创建使用指定工具和推理轮数的手写 ReAct Agent。"""
    # 返回绑定本次请求配置的新 Agent 对象。
    return ReactAgent(tools=tools, max_iterations=max_iterations)

# 定义便于路由调用的单轮文本问答函数。
def call(query: str, tools: Sequence[BaseTool] = ()) -> str:
    """为本次请求创建 Agent 并返回其最终文本答复。"""
    # 为本次调用创建只使用所传工具的 Agent。
    agent = create_react_agent(tools=tools)
    # 执行手写 ReAct 循环并返回最终答复。
    return agent.invoke(query)

# 定义便于路由调用的流式文本问答生成器。
def stream(query: str, tools: Sequence[BaseTool] = ()) -> Iterator[AgentStreamEvent]:
    """为本次请求创建 Agent 并逐段产出最终文本答复。"""
    # 为本次流式调用创建只使用所传工具的 Agent。
    agent = create_react_agent(tools=tools)
    # 流式执行手写 ReAct 循环并转发答复分块。
    yield from agent.stream(query)
