# 导入文件系统路径类型。
from pathlib import Path

# 定位 LangChain 项目根目录。
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# 定位仓库根目录。
REPOSITORY_ROOT = PROJECT_ROOT.parent


# 验证 README 展示全部 API 和启动方式。
def test_readme_documents_fastapi_demos() -> None:
    # 读取 LangChain 项目说明。
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    # 定义必须展示的命令和端点。
    required_text = [
        "uvicorn api.main:app",
        "/docs",
        "/api/v1/prompts/{template_type}/invoke",
        "/api/v1/stream/text",
        "/api/v1/stream/sse",
        "/api/v1/memory/chat",
        "/api/v1/structured/extract",
        "/api/v1/tools/chat",
        "/api/v1/mcp/chat",
        "/api/v1/skills",
    ]
    # 验证每项文档契约都存在。
    for text in required_text:
        # 报告具体缺失文本。
        assert text in readme


# 验证环境示例和运行数据忽略规则完整。
def test_environment_example_and_gitignore_cover_runtime_modes() -> None:
    # 读取环境变量示例。
    environment_example = (PROJECT_ROOT / ".env.example").read_text(
        encoding="utf-8"
    )
    # 读取仓库忽略规则。
    gitignore = (REPOSITORY_ROOT / ".gitignore").read_text(encoding="utf-8")
    # 验证两种记忆后端的配置入口。
    assert "MEMORY_BACKEND=" in environment_example
    # 验证 SQLite 文件配置入口。
    assert "MEMORY_SQLITE_PATH=" in environment_example
    # 验证 MCP 模式配置入口。
    assert "MCP_MODE=" in environment_example
    # 验证远程 MCP 地址配置入口。
    assert "MCP_REMOTE_URL=" in environment_example
    # 验证 SQLite 运行数据不会提交。
    assert "langchain-learn/data/*.sqlite*" in gitignore
    # 验证 pytest 临时目录不会污染 Git。
    assert "**/.pytest-tmp/" in gitignore


# 验证文档包含会话删除命令且依赖版本满足兼容和安全基线。
def test_readme_and_requirements_cover_reviewed_runtime_contracts() -> None:
    # 读取项目说明。
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    # 读取运行依赖清单。
    requirements = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")
    # 验证文档给出可复制的会话删除命令。
    assert "Invoke-RestMethod -Method Delete" in readme
    # 验证 LangChain 最低版本与代码使用的 Agent 接口一致。
    assert "langchain>=1.2,<2" in requirements
    # 验证 SQLite 检查点依赖避开旧版安全问题。
    assert "langgraph-checkpoint-sqlite>=3.1,<4" in requirements
