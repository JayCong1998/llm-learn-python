# FastAPI 车辆管理脚手架设计

## 目标

在现有 `fastapi-scaffold` 中实现一个单体分层 API：提供用户注册、登录与 JWT 认证；管理员可维护汽车品牌和车型；普通用户与匿名访问者只能查询品牌和车型。

## 范围

首版使用 SQLite、SQLAlchemy 与 Alembic。API 不包含前端页面、刷新令牌、找回密码、文件上传、软删除或多租户。项目保留现有健康检查和 `.env` 配置方式。

## 架构

应用维持 `api -> service -> repository -> model` 分层。路由层只处理 HTTP、请求/响应模型和依赖注入；服务层承载注册、认证、业务校验及授权后的用例；仓储层封装 SQLAlchemy 查询；模型层定义 SQLite 表；schema 层定义 Pydantic DTO。`core` 提供设置、数据库会话、密码哈希、JWT 与权限依赖。

数据库会话通过 FastAPI `Depends` 按请求创建并在请求结束时关闭。Alembic 负责创建和升级表结构。启动时不自动创建管理员；管理员角色需由迁移后的初始化命令或直接数据库数据建立，首版附带可重复执行的初始化脚本创建由环境变量配置的管理员。

## 数据模型

`User`：`id`、唯一 `username`、唯一 `email`、`password_hash`、`role`（`admin` 或 `user`）、创建时间。

`Brand`：`id`、唯一 `name`、`country`、可选 `description`、创建与更新时间。

`CarModel`：`id`、`name`、`year`、`price`、`brand_id`、创建与更新时间。`brand_id` 外键关联 `Brand`；一个品牌可有多个车型。品牌删除在仍有关联车型时返回业务错误，避免隐式级联删除。

## API 与权限

`POST /auth/register` 创建默认 `user` 角色账号，重复用户名或邮箱返回 409；`POST /auth/login` 验证账号密码，返回 Bearer JWT。

`GET /brands`、`GET /brands/{id}`、`GET /car-models`、`GET /car-models/{id}` 为公开读接口，支持车型按 `brand_id` 过滤与基础分页。

`POST`、`PUT`、`DELETE` 的 `/brands` 与 `/car-models` 端点要求有效 Bearer JWT 且角色为 `admin`。未登录返回 401；已登录但非管理员返回 403；资源不存在返回 404；数据不合法返回 422。

## 安全与配置

密码只保存 bcrypt 哈希，绝不返回或写入日志。JWT 使用 HS256，密钥和过期分钟数从 `.env` 读取；`.env.example` 仅提供安全的开发示例，生产环境必须替换密钥。SQLite 数据库 URL 默认指向模块目录的 `data/app.db`，可由环境变量覆盖。

## 测试

测试使用独立临时 SQLite 数据库，避免污染开发数据库。覆盖注册、重复注册、登录、错误密码、普通用户读权限、普通用户写入被拒、管理员品牌 CRUD、管理员车型 CRUD、车型所属品牌校验、品牌有车型时不可删除，以及现有健康检查与配置覆盖行为。

## 验收标准

从 `fastapi-scaffold` 创建虚拟环境、安装依赖、执行迁移与管理员初始化后，可启动 Uvicorn 并通过 OpenAPI 文档操作全部接口。完整 pytest 套件通过；每条新增或修改的 Python 有效代码行遵守仓库要求，前一行附带准确简短的中文独立行注释。
