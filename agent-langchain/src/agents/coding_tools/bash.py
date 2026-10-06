# 导入系统信息和子进程执行模块。
import os
import subprocess

# 导入 LangChain 工具装饰器以注册结构化工具。
from langchain_core.tools import tool

# 导入共享命令校验、超时、输出限制和工作区配置。
from agents.coding_tools.common import (
    COMMAND_TIMEOUT_SECONDS,
    limit_output,
    safe_file_deletion,
    validate_shell_command,
    WORKSPACE_ROOT,
)

# 声明在项目工作区执行命令的 Bash 工具。
@tool
# 在本地 shell 中执行用户提供的项目命令。
def Bash(command: str, timeout_seconds: int = COMMAND_TIMEOUT_SECONDS) -> str:
    """在项目工作区运行 shell 命令。command 是要执行的命令；timeout_seconds 是超时秒数，默认 30 秒并限制在 1 到 120 秒。"""
    # 将命令超时限制在 1 到 120 秒之间。
    timeout = min(max(timeout_seconds, 1), 120)
    # 将简单文件删除命令交由工作区范围校验器处理。
    handled, deletion_result = safe_file_deletion(command)
    # 返回受控删除结果且不启动 shell 子进程。
    if handled:
        # 返回安全删除成功或拒绝执行的结果。
        return deletion_result
    # 在启动子进程前拦截已知高风险命令。
    rejection = validate_shell_command(command)
    # 对违反策略的命令返回提示且不启动 shell。
    if rejection:
        # 返回安全策略拒绝原因。
        return rejection
    # 根据操作系统选择可用 shell 启动方式。
    shell_command = ["cmd.exe", "/c", command] if os.name == "nt" else ["/bin/bash", "-lc", command]
    # 在工作区内运行命令并捕获两个输出流。
    try:
        # 执行命令并限制运行时长及输出编码。
        result = subprocess.run(
            shell_command,
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    # 将超时异常转为可读工具结果。
    except subprocess.TimeoutExpired:
        # 返回本次命令使用的超时限制。
        return f"命令超时（限制 {timeout} 秒）。"
    # 合并标准输出、错误输出和退出码。
    output = f"{result.stdout}{result.stderr}\n退出码：{result.returncode}".strip()
    # 限制命令结果传回模型的字符数。
    return limit_output(output)
