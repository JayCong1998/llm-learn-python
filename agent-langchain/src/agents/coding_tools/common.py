# 导入正则表达式和路径类型以校验工作区操作。
import os
import re
import shlex
from pathlib import Path

# 定义编程工具唯一允许访问的项目工作目录。
WORKSPACE_ROOT = Path(__file__).resolve().parents[3] / "workdir"
# 限制单个工具输出的最大字符数。
MAX_OUTPUT_CHARS = 20_000
# 限制 shell 命令的默认运行时长。
COMMAND_TIMEOUT_SECONDS = 30
# 定义禁止文件工具访问的敏感路径名称。
_BLOCKED_PATH_PARTS = {".git", ".ssh", ".aws", ".azure", ".gnupg", "secrets"}
# 定义禁止直接读取或修改的凭据文件名称。
_BLOCKED_FILE_NAMES = {".env", ".env.local", "id_rsa", "id_ed25519", "credentials"}


# 将用户路径解析为工作区内的绝对路径并拒绝越界访问。
def resolve_workspace_path(path: str) -> Path:
    # 解析相对路径并规范化符号链接与父目录。
    resolved_path = (WORKSPACE_ROOT / path).resolve()
    # 检查解析后的路径是否仍处于工作区目录内。
    if not resolved_path.is_relative_to(WORKSPACE_ROOT):
        # 对越界路径抛出可读错误。
        raise ValueError("路径超出允许的项目工作区。")
    # 检查路径中是否包含禁止访问的敏感目录。
    if any(part.lower() in _BLOCKED_PATH_PARTS for part in resolved_path.relative_to(WORKSPACE_ROOT).parts):
        # 拒绝访问凭据存储或版本控制目录。
        raise ValueError("该路径属于禁止访问的敏感目录。")
    # 检查目标文件是否属于凭据或私钥文件。
    if resolved_path.name.lower() in _BLOCKED_FILE_NAMES or resolved_path.suffix.lower() in {".pem", ".p12", ".pfx", ".key"}:
        # 拒绝读取或修改敏感文件。
        raise ValueError("该路径属于禁止访问的凭据或密钥文件。")
    # 返回通过工作区边界校验的绝对路径。
    return resolved_path


# 定义 Bash 中不允许执行的高风险命令模式。
_BLOCKED_COMMAND_PATTERNS = (
    r"\b(?:rm|rd|rmdir|del|erase|format|diskpart|shutdown|reboot|poweroff|mkfs|dd)\b",
    r"\bRemove-Item\b[^\r\n]*-(?:Recurse|Force)",
    r"\b(?:git\s+reset\s+--hard|git\s+clean\s+-[a-z]*f|git\s+push\b[^\r\n]*(?:--force\b|-f\b)|git\s+checkout\s+--\s|git\s+restore\s+\.)",
    r"\b(?:sudo|runas|Start-Process\b[^\r\n]*-Verb\s+RunAs|Set-ExecutionPolicy)\b",
    r"\b(?:chmod\s+777|chown\s+-R)\b",
    r"\b(?:Invoke-Expression|\biex\b)\b",
    r"\b(?:DROP\s+DATABASE|DROP\s+SCHEMA|TRUNCATE\s+TABLE)\b",
    r"\b(?:curl|wget|iwr|Invoke-WebRequest)\b[^\r\n]*(?:\||;|&&)\s*(?:sh|bash|python|pwsh|powershell)\b",
    r"(?:^|[\s\\/])(?:\.env(?:\.[\w.-]+)?|\.ssh|\.aws|id_rsa|id_ed25519)(?:$|[\s\\/])",
)


# 解析只删除单个普通文件的受限命令。
def safe_file_deletion(command: str) -> tuple[bool, str]:
    # 仅识别不含 shell 控制符的单条删除命令。
    if re.search(r"[;&|`\n\r<>]", command):
        # 将带组合语法的删除命令交由高风险命令拦截器拒绝。
        return False, ""
    # 尝试解析简单命令行参数及引号。
    try:
        # 使用标准 shell 词法规则拆分命令。
        arguments = shlex.split(command, posix=True)
    # 对无法解析的引号语法返回受限删除失败。
    except ValueError:
        # 标记该输入是删除命令且无法安全解析。
        return True, "删除命令格式无效，已拒绝执行。"
    # 对空输入不按删除命令处理。
    if not arguments:
        # 返回未识别状态。
        return False, ""
    # 识别受支持的普通文件删除命令名称。
    command_name = Path(arguments[0]).name.lower()
    # 对非删除命令返回未识别状态。
    if command_name not in {"rm", "del", "erase", "remove-item"}:
        # 返回未识别状态。
        return False, ""
    # 只允许单个目标且不允许选项、通配符或额外参数。
    if len(arguments) != 2 or arguments[1].startswith(("-", "/")) or any(char in arguments[1] for char in "*?[]"):
        # 拒绝递归、强制、通配符及多目标删除。
        return True, "仅允许删除工作目录内单个明确指定的文件。"
    # 校验并解析删除目标路径。
    try:
        # 解析目标并执行工作区与敏感路径校验。
        target_path = resolve_workspace_path(arguments[1])
    # 拒绝越界或敏感文件目标。
    except ValueError as error:
        # 返回路径安全校验失败原因。
        return True, f"删除目标被安全策略拒绝：{error}"
    # 拒绝目录、缺失路径及非普通文件目标。
    if not target_path.is_file():
        # 说明只允许删除已存在的普通文件。
        return True, "删除目标必须是工作目录内已存在的普通文件。"
    # 删除通过校验的单个普通文件。
    target_path.unlink()
    # 返回删除完成的相对路径。
    return True, f"已删除工作目录内文件：{target_path.relative_to(WORKSPACE_ROOT)}"


# 拒绝常见的系统破坏、提权和不可逆命令。
def validate_shell_command(command: str) -> str | None:
    # 遍历已知高风险命令模式。
    for pattern in _BLOCKED_COMMAND_PATTERNS:
        # 对命令文本进行大小写不敏感的模式检查。
        if re.search(pattern, command, re.IGNORECASE):
            # 返回统一的高风险命令拦截提示。
            return "命令被安全策略拦截：包含禁止的高风险操作。"
    # 拒绝其他常见的 shell 递归删除参数写法。
    if re.search(r"\b(?:rm|del|erase|remove-item)\b[^\r\n]*(?:-r\b|-rf\b|-fr\b|/s\b|--recursive|--force)", command, re.IGNORECASE):
        # 返回删除范围过大的拦截说明。
        return "命令被安全策略拦截：不允许递归或强制删除。"
    # 允许未匹配禁止规则的命令继续执行。
    return None


# 统一截断过长工具输出以控制模型上下文大小。
def limit_output(text: str) -> str:
    # 在输出超限时保留开头并附加截断说明。
    if len(text) > MAX_OUTPUT_CHARS:
        # 返回受限文本和总字符数提示。
        return f"{text[:MAX_OUTPUT_CHARS]}\n...（输出已截断，共 {len(text)} 个字符）"
    # 原样返回长度合适的文本。
    return text
