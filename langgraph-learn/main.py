# 导入配置异常和图构建函数。
from app import ConfigurationError, build_graph


# 定义命令行程序的主函数。
def main() -> int:
    # 尝试构建并执行一次工作流。
    try:
        # 使用固定学习问题调用已编译的图。
        result = build_graph().invoke(
            {"question": "请用一句话解释 LangGraph 的用途。", "answer": ""}
        )
        # 输出图最终状态中的回答。
        print(result["answer"])
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
