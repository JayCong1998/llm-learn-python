# FastAPI 分层分包迁移设计

## 目标

将 `fastapi-scaffold` 从 API 路由同时承载 HTTP、业务规则和数据访问的结构，彻底迁移为 `api`、`services`、`repositories`、`models`、`schemas` 与 `core` 的职责分层；对外 API 契约和现有认证授权行为保持不变。

## 目录与职责

```text
fastapi-scaffold/app/
  api/             # 路径、依赖注入、HTTP 异常与响应声明
  services/        # 认证、品牌、车型的业务编排和事务边界
  repositories/    # SQLAlchemy 查询、实体新增、删除与刷新
  models/          # ORM 表映射与关系
  schemas/         # Pydantic 入参与出参模型
  core/            # 配置、数据库连接、安全算法及共享依赖
```

`api` 层可以依赖 `services`、`schemas` 和 FastAPI；不得导入 SQLAlchemy 查询构造器或 ORM 模型。`services` 层依赖 `repositories`、`models`、`schemas`、数据库会话和领域异常；它管理提交、回滚和业务规则。`repositories` 层只依赖 ORM 与 SQLAlchemy，返回实体或查询结果，不创建 HTTP 异常。

## 组件设计

- `repositories/user_repository.py`：按用户名查找、按用户名或邮箱查找、持久化用户。
- `repositories/brand_repository.py`：查询品牌、按名称查找、持久化和删除品牌、查询关联车型是否存在。
- `repositories/car_model_repository.py`：查询、筛选分页、持久化和删除车型。
- `services/auth_service.py`：注册冲突判断、密码散列、登录验证和令牌生成。
- `services/brand_service.py`：品牌不存在、名称冲突、关联车型导致的删除冲突，以及品牌的创建、修改和删除事务。
- `services/car_model_service.py`：车型和品牌存在性校验、车型的筛选分页、创建、修改和删除事务。

服务层将使用项目内部的领域异常来表达未找到、冲突及认证失败；API 层统一将这些异常翻译为当前的 HTTP 状态码和中文错误信息。权限依赖 `get_current_user` 与 `require_admin` 保持在 `core/dependencies.py`，路由仍用依赖声明进行访问控制。

## 数据流

请求经由 API 路由校验为 schema，路由调用 service。service 使用 repository 读写 ORM 实体，在成功写入时提交事务；repository 不提交事务。service 返回 ORM 实体，路由利用既有 `response_model` 序列化响应。service 失败时抛领域异常，路由转换为原有 HTTP 响应。

## 兼容性与错误处理

- 保持所有 URL、请求字段、响应字段和状态码不变。
- 保持现有规则：品牌、车型路由要求登录；写入操作要求管理员。
- 保持重复用户名/邮箱和重复品牌名返回 409；不存在资源或品牌返回 404；错误登录返回 401；普通用户写入返回 403；有关联车型的品牌删除返回 409。
- 每次写入失败时回滚会话，避免复用会话处于失败事务状态。

## 测试策略

保留现有 API 集成测试以验证契约。新增 repository 测试验证查询与持久化边界，新增 service 测试验证业务规则、提交及失败回滚。每个新增或移动的 Python 有效代码行之前均添加准确、简短的中文独立行注释，遵守仓库规则。
