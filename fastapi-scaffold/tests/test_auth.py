# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient
# 导入 pytest 测试框架。
import pytest
# 导入 SQLAlchemy 测试引擎创建函数。
from sqlalchemy import create_engine
# 导入 SQLAlchemy 会话工厂。
from sqlalchemy.orm import sessionmaker
# 导入 SQLAlchemy 单连接池实现。
from sqlalchemy.pool import StaticPool

# 导入数据库基类。
from app.core.database import Base
# 导入应用数据库依赖。
from app.core.database import get_db
# 导入应用实例。
from app.main import app
# 导入用户模型以注册数据表。
from app.models.user import User


# 创建跨线程共享单连接的测试内存数据库引擎。
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
# 创建测试数据库的会话工厂。
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 为每个测试重建数据表并提供 HTTP 客户端。
@pytest.fixture
def test_client():
    # 删除上一轮测试的数据表。
    Base.metadata.drop_all(bind=engine)
    # 创建当前测试所需的数据表。
    Base.metadata.create_all(bind=engine)

    # 定义覆盖生产数据库依赖的生成器。
    def override_get_db():
        # 创建测试数据库会话。
        database_session = TestingSessionLocal()
        # 确保测试请求结束后关闭会话。
        try:
            # 为路由提供测试数据库会话。
            yield database_session
        # 无论请求结果如何都关闭会话。
        finally:
            # 释放测试数据库连接。
            database_session.close()

    # 为应用注入测试数据库依赖。
    app.dependency_overrides[get_db] = override_get_db
    # 创建测试客户端。
    client = TestClient(app)
    # 返回可调用的测试客户端。
    yield client
    # 清理依赖覆盖避免影响其他测试。
    app.dependency_overrides.clear()


# 验证注册接口默认创建普通用户且不回传密码哈希。
def test_register_creates_default_user(test_client):
    # 发送注册请求。
    response = test_client.post("/auth/register", json={"username": "alice", "email": "alice@example.com", "password": "secret-password"})

    # 断言注册成功。
    assert response.status_code == 201
    # 断言响应返回用户名。
    assert response.json()["data"]["username"] == "alice"
    # 断言响应返回普通用户角色。
    assert response.json()["data"]["role"] == "user"
    # 断言响应不会暴露密码哈希。
    assert "password_hash" not in response.json()["data"]


# 验证注册和登录均接受与默认管理员一致的五位密码。
def test_auth_accepts_five_character_password(test_client):
    # 使用五位密码注册用户。
    register_response = test_client.post("/auth/register", json={"username": "admin", "email": "admin@qq.com", "password": "admin"})
    # 使用相同的五位密码登录。
    login_response = test_client.post("/auth/login", json={"username": "admin", "password": "admin"})

    # 断言注册请求成功。
    assert register_response.status_code == 201
    # 断言登录请求成功。
    assert login_response.status_code == 200


# 验证重复用户名或邮箱会被拒绝。
def test_register_rejects_duplicate_username_or_email(test_client):
    # 定义初始注册信息。
    payload = {"username": "alice", "email": "alice@example.com", "password": "secret-password"}
    # 创建初始用户。
    test_client.post("/auth/register", json=payload)
    # 使用重复用户名注册。
    username_response = test_client.post("/auth/register", json={**payload, "email": "other@example.com"})
    # 使用重复邮箱注册。
    email_response = test_client.post("/auth/register", json={**payload, "username": "other"})

    # 断言重复用户名返回冲突状态。
    assert username_response.status_code == 409
    # 断言重复邮箱返回冲突状态。
    assert email_response.status_code == 409


# 验证登录返回 Bearer JWT 且错误密码被拒绝。
def test_login_returns_bearer_token_and_rejects_invalid_password(test_client):
    # 注册可登录用户。
    test_client.post("/auth/register", json={"username": "alice", "email": "alice@example.com", "password": "secret-password"})
    # 发送正确登录请求。
    login_response = test_client.post("/auth/login", json={"username": "alice", "password": "secret-password"})
    # 发送错误密码登录请求。
    invalid_response = test_client.post("/auth/login", json={"username": "alice", "password": "wrong-password"})

    # 断言正确登录成功。
    assert login_response.status_code == 200
    # 断言响应符合 Bearer Token 格式。
    assert login_response.json()["data"]["token_type"] == "bearer"
    # 断言响应包含访问令牌。
    assert login_response.json()["data"]["access_token"]
    # 断言错误密码返回未认证状态。
    assert invalid_response.status_code == 401
    # 断言错误密码响应使用统一错误信封。
    assert invalid_response.json() == {"code": 401, "message": "用户名或密码错误", "data": None}


# 验证普通用户无法调用仅管理员允许的写入端点。
def test_regular_user_is_forbidden_from_admin_write_endpoint(test_client):
    # 注册普通用户。
    test_client.post("/auth/register", json={"username": "alice", "email": "alice@example.com", "password": "secret-password"})
    # 获取普通用户访问令牌。
    login_response = test_client.post("/auth/login", json={"username": "alice", "password": "secret-password"})
    # 读取访问令牌。
    token = login_response.json()["data"]["access_token"]
    # 使用普通用户令牌调用管理员写入端点。
    response = test_client.post("/auth/admin-probe", headers={"Authorization": f"Bearer {token}"})

    # 断言普通用户被禁止写入。
    assert response.status_code == 403
    # 断言权限错误响应使用统一错误信封。
    assert response.json() == {"code": 403, "message": "需要管理员权限", "data": None}
