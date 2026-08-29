# 导入配置异常和提问函数。
from app import ConfigurationError, ask_question


# 定义命令行程序的主函数。
def main() -> int:
    # 尝试执行一次模型提问。
    try:
        # 输出模型对固定学习问题的回答。
        print(ask_question("请用一句话解释 LangChain 的用途。"))
    # 单独处理缺少配置的预期错误。
    except ConfigurationError as error:
        # 输出可操作的配置错误信息。
        print(f"Configuration error: {error}")
        # 返回非零状态码表示执行失败。
        return 1
    # 捕获模型请求期间发生的其他异常。
    except Exception as error:
        # 输出模型调用失败的错误信息。
        print(f"Model request failed: {error}")
        # 返回非零状态码表示执行失败。
        return 1
    # 返回零状态码表示执行成功。
    return 0


# 仅在直接运行本文件时启动程序。
if __name__ == "__main__":
    # 使用主函数的返回值作为进程退出码。
    raise SystemExit(main())
