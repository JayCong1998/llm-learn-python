# fastapi-scaffold

面向 Java 开发者的 FastAPI 单体分层 API 脚手架，提供 JWT 登录注册、管理员角色控制、汽车品牌和车型管理。

## 环境与安装

需要 Python 3.11+。在 PowerShell 中执行：

```powershell
cd fastapi-scaffold
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` 中至少应修改 `JWT_SECRET_KEY`，并为创建管理员配置 `ADMIN_USERNAME`、`ADMIN_EMAIL` 和 `ADMIN_PASSWORD`。

## 初始化数据库

项目默认使用 SQLite，数据库路径为 `data/app.db`。首次运行前执行迁移：

```powershell
alembic upgrade head
```

迁移会创建 `users`、`brands` 和 `car_models` 三张表。开发新的模型变更后，可生成迁移并应用：

```powershell
alembic revision --autogenerate -m "描述变更"
alembic upgrade head
```

## 创建管理员

迁移完成后，从 `.env` 读取管理员配置并执行：

```powershell
python -m scripts.create_admin
```

脚本可重复执行；若相同用户名或邮箱已存在，会跳过创建，不会覆盖已有账户。

## 启动与登录

```powershell
uvicorn app.main:app --reload
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

## API 概览

| 资源 | 公开读取 | 管理员写入 |
| --- | --- | --- |
| 品牌 | `GET /brands`、`GET /brands/{brand_id}` | `POST /brands`、`PUT /brands/{brand_id}`、`DELETE /brands/{brand_id}` |
| 车型 | `GET /car-models`、`GET /car-models/{car_model_id}` | `POST /car-models`、`PUT /car-models/{car_model_id}`、`DELETE /car-models/{car_model_id}` |

普通用户和未登录访客只能查询品牌、车型列表或详情；只有角色为 `admin` 的账户能创建、修改或删除数据。

## 运行测试

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
