"""安全计算、时间工具和 Agent 调用轨迹提取。"""

# 导入抽象语法树解析工具。
import ast
# 导入日期时间类型。
from datetime import datetime
# 导入基础运算符函数。
import operator
# 导入通用对象和可调用类型。
from typing import Any, Callable
# 导入标准时区数据库。
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# 导入 LangChain 助手消息类型。
from langchain_core.messages import AIMessage, BaseMessage
# 导入 LangChain 工具装饰器。
from langchain_core.tools import tool

# 导入兼容 Agent 工厂。
from api.core.agents import create_agent_runtime
# 导入安全上游异常。
from api.core.errors import UpstreamServiceError
# 导入 Agent 对外响应类型。
from api.core.schemas import AgentReply, ToolCallTrace

# 定义计算结果允许的最大绝对值。
MAX_ABSOLUTE_VALUE = 1_000_000_000_000

# 定义允许的二元运算符。
ALLOWED_BINARY_OPERATORS = {
    # 允许加法。
    ast.Add: operator.add,
    # 允许减法。
    ast.Sub: operator.sub,
    # 允许乘法。
    ast.Mult: operator.mul,
    # 允许除法。
    ast.Div: operator.truediv,
}

# 定义允许的一元运算符。
ALLOWED_UNARY_OPERATORS = {
    # 允许一元正号。
    ast.UAdd: operator.pos,
    # 允许一元负号。
    ast.USub: operator.neg,
}


# 计算只含数字、括号和四则运算的表达式。
def evaluate_expression(expression: str) -> int | float:
    # 拒绝过长输入以限制解析成本。
    if len(expression) > 200:
        # 抛出明确安全校验错误。
        raise ValueError("表达式过长")
    # 尝试以表达式模式解析语法树。
    try:
        # 解析用户表达式但不执行代码。
        tree = ast.parse(expression, mode="eval")
    # 捕获无效 Python 表达式语法。
    except SyntaxError as error:
        # 转换为统一输入错误。
        raise ValueError("表达式语法无效") from error
    # 计算白名单语法树节点。
    result = _evaluate_node(tree.body)
    # 验证最终结果大小。
    return _bounded_number(result)


# 递归计算单个白名单语法树节点。
def _evaluate_node(node: ast.AST) -> int | float:
    # 接受非布尔的整数或浮点常量。
    if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
        # 返回经过范围校验的常量。
        return _bounded_number(node.value)
    # 处理白名单二元运算。
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_BINARY_OPERATORS:
        # 递归计算左操作数。
        left = _evaluate_node(node.left)
        # 递归计算右操作数。
        right = _evaluate_node(node.right)
        # 调用固定运算函数。
        result = ALLOWED_BINARY_OPERATORS[type(node.op)](left, right)
        # 返回经过范围校验的结果。
        return _bounded_number(result)
    # 处理白名单一元运算。
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_UNARY_OPERATORS:
        # 递归计算一元操作数。
        operand = _evaluate_node(node.operand)
        # 调用固定一元运算函数。
        result = ALLOWED_UNARY_OPERATORS[type(node.op)](operand)
        # 返回经过范围校验的结果。
        return _bounded_number(result)
    # 拒绝函数调用、属性访问和其他语法。
    raise ValueError("表达式包含不允许的语法")


# 校验数值结果处于教学工具的安全范围。
def _bounded_number(value: int | float) -> int | float:
    # 拒绝非有限或绝对值过大的结果。
    if not isinstance(value, (int, float)) or abs(value) > MAX_ABSOLUTE_VALUE:
        # 抛出结果范围错误。
        raise ValueError("计算结果超出允许范围")
    # 返回经过范围校验的数字。
    return value


# 将安全计算器注册为 LangChain 工具。
@tool
def safe_calculate(expression: str) -> str:
    """计算只含数字、括号和四则运算符的表达式。"""
    # 计算表达式并转换为模型易读文本。
    return str(evaluate_expression(expression))


# 将当前时间查询注册为 LangChain 工具。
@tool
def current_time(timezone_name: str = "Asia/Shanghai") -> str:
    """返回指定 IANA 时区的当前时间。"""
    # 尝试加载白名单格式的 IANA 时区。
    try:
        # 创建标准时区对象。
        timezone = ZoneInfo(timezone_name)
    # 捕获未知时区名称。
    except ZoneInfoNotFoundError as error:
        # 抛出工具可解释的输入错误。
        raise ValueError("未知时区名称") from error
    # 返回带时区偏移的秒级时间。
    return datetime.now(timezone).isoformat(timespec="seconds")


# 从 Agent 消息中提取安全的最终回答和工具调用。
def build_agent_reply(messages: list[BaseMessage]) -> AgentReply:
    # 初始化工具调用摘要列表。
    traces: list[ToolCallTrace] = []
    # 遍历全部 Agent 消息。
    for message in messages:
        # 只处理助手消息中的结构化工具请求。
        if isinstance(message, AIMessage):
            # 遍历助手消息的工具调用。
            for call in message.tool_calls:
                # 保存工具名和模型参数。
                traces.append(
                    ToolCallTrace(
                        name=str(call["name"]),
                        arguments=dict(call["args"]),
                    )
                )
    # 逆序寻找最后一条带正文的助手消息。
    for message in reversed(messages):
        # 只选择非空助手正文。
        if isinstance(message, AIMessage) and message.content:
            # 返回最终正文和调用摘要。
            return AgentReply(answer=str(message.content), tool_calls=traces)
    # 拒绝缺少最终助手回答的异常状态。
    raise UpstreamServiceError("Agent 未返回最终回答")


# 定义安全本地工具 Agent 服务。
class ToolService:
    # 初始化模型和固定工具 Agent。
    def __init__(
        self,
        model: Any,
        agent_factory: Callable[..., Any] = create_agent_runtime,
    ) -> None:
        # 尝试创建只包含安全固定工具的 Agent。
        try:
            # 保存已经初始化的本地工具 Agent。
            self.agent = agent_factory(
                model=model,
                tools=[safe_calculate, current_time],
                system_prompt="需要计算或时间信息时必须调用已提供的工具。",
            )
        # 捕获 Agent 工厂初始化异常。
        except Exception as error:
            # 映射为不泄露内部细节的上游错误。
            raise UpstreamServiceError("本地工具 Agent 初始化失败") from error

    # 让 Agent 回答并返回工具调用摘要。
    def chat(self, question: str) -> AgentReply:
        # 尝试调用工具 Agent。
        try:
            # 提交当前用户问题。
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": question}]}
            )
            # 提取安全对外响应。
            return build_agent_reply(result["messages"])
        # 保留已经清理过的上游异常。
        except UpstreamServiceError:
            # 继续抛出稳定异常。
            raise
        # 捕获其他 Agent 或工具异常。
        except Exception as error:
            # 映射为不泄露内部细节的上游错误。
            raise UpstreamServiceError("本地工具调用失败") from error
