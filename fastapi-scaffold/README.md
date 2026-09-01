# fastapi-scaffold

面向 Java 开发者的 FastAPI 单体分层 API 脚手架，提供 JWT 登录注册、用户 LLM 对话与调用审计。

## 分层结构

`app/api` 仅负责 HTTP 路由、依赖声明和错误响应映射；`app/services` 承担业务规则与事务边界；`app/repositories` 负责 SQLAlchemy 数据访问。`models`、`schemas` 与 `core` 分别保留 ORM、接口模型和基础设施职责。

## 快速启动

需要 Python 3.11+。以下命令均应在项目根目录 `fastapi-scaffold` 中的 PowerShell 执行。

首次运行时依次执行：

```powershell
cd fastapi-scaffold
python -m venv \.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m scripts.create_admin
python -m uvicorn app.main:app --reload
```

`.env` 中至少应修改 `JWT_SECRET_KEY`，并为创建管理员配置 `ADMIN_USERNAME`、`ADMIN_EMAIL` 和 `ADMIN_PASSWORD`。

启动成功后访问 [Swagger UI](http://127.0.0.1:8000/docs)，可直接在浏览器中调用和测试接口；健康检查地址为 `http://127.0.0.1:8000/health`。

### `python -m` 的含义

`python -m 模块名` 表示由当前选定的 Python 解释器执行指定模块。推荐始终使用这种形式，例如 `python -m pip`、`python -m pytest` 和 `python -m uvicorn`，这样可以确保命令使用当前虚拟环境 `.venv` 中安装的依赖，避免混用系统 Python。

### 常用命令

```powershell
# 激活虚拟环境（每次新开终端后执行）
.\.venv\Scripts\Activate.ps1

# 安装或更新项目依赖
python -m pip install -r requirements.txt

# 启动开发服务器；修改 Python 代码后会自动重启
python -m uvicorn app.main:app --reload

# 运行全部测试
python -m pytest -q

# 只运行聊天接口测试
python -m pytest tests/test_chat.py -q

# 应用所有数据库迁移
alembic upgrade head

# 根据 ORM 模型变更生成迁移文件，再应用迁移
alembic revision --autogenerate -m "描述变更"
alembic upgrade head

# 从 .env 中读取配置，创建管理员（可重复执行）
python -m scripts.create_admin
```

## 初始化数据库

项目默认使用 SQLite，数据库路径为 `data/app.db`。首次运行前执行迁移：

```powershell
alembic upgrade head
```

迁移会将既有 `users` 表升级为 `user`，并创建 `chat_conversation`、`chat_message` 与 `llm_call_log` 表；最新迁移会移除已废弃的汽车品牌和车型表。开发新的模型变更后，可生成迁移并应用：

```powershell
alembic revision --autogenerate -m "描述变更"
alembic upgrade head
```

## 创建管理员

迁移完成后，从 `.env` 读取管理员配置并执行：

```powershell
python -m scripts.create_admin
```

### LLM 对话持久化

`user`、`chat_conversation`、`chat_message` 与 `llm_call_log` 都包含 `created_at`、`updated_at`、`lock_version` 与 `deleted` 字段。`llm_call_log` 仅关联模型生成的一条 `assistant` 消息；工具调用和工具结果只保留在单次请求的内存上下文中，不写入数据库。

脚本可重复执行；若相同用户名或邮箱已存在，会跳过创建，不会覆盖已有账户。

## 启动与登录

```powershell
python -m uvicorn app.main:app --reload
```

启动后访问 [Swagger UI](http://127.0.0.1:8000/docs)，或访问 `http://127.0.0.1:8000/health` 进行健康检查。

注册普通用户：

```http
POST /auth/register
Content-Type: application/json

{"username":"alice","email":"alice@example.com","password":"secret-password"}
```

登录获取 JWT：

```http
POST /auth/login
Content-Type: application/json

{"username":"admin","password":"change-this-admin-password"}
```

登录响应中的 `access_token` 需要以 `Authorization: Bearer <access_token>` 请求头传给管理员写入接口。

## 聊天 API

认证后可调用 `POST /chat/conversations` 创建会话，`POST /chat/conversations/{id}/messages` 发送消息，`GET /chat/conversations` 与 `GET /chat/conversations/{id}` 查询历史，`DELETE /chat/conversations/{id}` 逻辑删除会话。

在 `.env` 配置 `LLM_BASE_URL`、`LLM_API_KEY` 与 `LLM_MODEL` 后，服务会调用 OpenAI 兼容的 `/chat/completions` 接口。

## 运行测试

```powershell
python -m pytest -q
```
