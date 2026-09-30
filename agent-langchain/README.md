# Agent LangChain

基于 Python 3.13、FastAPI、LangChain 和通义千问（Qwen）的 Agent 项目骨架。

## 环境准备

项目解释器要求为 Python 3.13。安装项目及开发依赖：

```powershell
python -m pip install -e ".[dev]"
```

## 配置

复制 `.env.example` 为 `.env`，填入 DashScope API Key。Qwen 使用 DashScope 的 OpenAI 兼容接口。

## 启动

```powershell
uvicorn agent_langchain.main:app --app-dir src --reload
```

健康检查地址：`http://127.0.0.1:8000/health`。

