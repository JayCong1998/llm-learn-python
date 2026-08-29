"""运行全部提示词工程示例。"""

# 导入返回进程状态码的类型支持。
from collections.abc import Callable
# 导入命令行退出工具。
import sys

# 导入模型配置异常和提示词调用函数。
from .app import ConfigurationError, get_model, invoke_prompt
# 导入全部提示词模板构造函数。
from .examples import (
    build_chat_prompt,
    build_few_shot_chat_prompt,
    build_few_shot_prompt,
    build_history_prompt,
    build_selector_prompt,
    build_text_prompt,
)


# 定义示例构造函数的类型别名。
PromptFactory = Callable[[], object]


# 定义顺序执行全部提示词工程示例的函数。
def run_examples() -> None:
    """创建模型并依次打印六类提示词模板的模型回复。"""
    # 创建配置好的聊天模型实例。
    model = get_model()
    # 定义示例名称、提示词构造函数和变量字典。
    examples: list[tuple[str, PromptFactory, dict[str, object]]] = [
        ("PromptTemplate", build_text_prompt, {"topic": "向量数据库"}),
        ("ChatPromptTemplate", build_chat_prompt, {"question": "什么是提示词工程？"}),
        (
            "MessagesPlaceholder",
            build_history_prompt,
            {"history": [], "question": "请用一句话继续说明。"},
        ),
        ("FewShotPromptTemplate", build_few_shot_prompt, {"text": "下雨"}),
        (
            "FewShotChatMessagePromptTemplate",
            build_few_shot_chat_prompt,
            {"question": "下雪"},
        ),
        ("LengthBasedExampleSelector", build_selector_prompt, {"text": "多云"}),
    ]
    # 按定义顺序执行每个示例。
    for name, factory, values in examples:
        # 输出当前示例的名称。
        print(f"\n=== {name} ===")
        # 创建当前示例的提示词模板。
        prompt = factory()
        # 输出模型对当前提示词的回复。
        print(invoke_prompt(prompt, model, values))


# 定义命令行入口函数。
def main() -> int:
    """运行示例并将配置或服务错误转为退出状态码。"""
    # 尝试执行全部模型调用示例。
    try:
        # 运行全部提示词工程示例。
        run_examples()
    # 捕获缺少模型配置的可预期错误。
    except ConfigurationError as error:
        # 输出指导用户配置环境变量的错误信息。
        print(f"配置错误：{error}")
        # 返回表示失败的退出状态码。
        return 1
    # 捕获网络或模型服务调用期间发生的错误。
    except Exception as error:
        # 输出简洁的模型调用错误信息。
        print(f"模型调用失败：{error}")
        # 返回表示失败的退出状态码。
        return 1
    # 返回表示成功的退出状态码。
    return 0


# 在直接执行模块时启动命令行入口。
if __name__ == "__main__":
    # 使用入口状态码结束当前进程。
    sys.exit(main())
