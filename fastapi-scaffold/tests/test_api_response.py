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
# 导入数据库依赖。
from app.core.database import get_db
# 导入应用实例。
from app.main import app
# 导入用户模型以注册数据表。
from app.models.user import User


# 为每个测试重建数据表并提供 HTTP 客户端。
@pytest.fixture
# 定义测试客户端夹具。
def test_client():
    # 创建跨线程共享单连接的测试内存数据库引擎。
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    # 创建测试数据库会话工厂。
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # 删除上一轮测试的数据表。
    Base.metadata.drop_all(bind=engine)
    # 创建当前测试所需的数据表。
    Base.metadata.create_all(bind=engine)

    # 定义覆盖生产数据库依赖的生成器。
    def override_get_db():
        # 创建测试数据库会话。
        database_session = testing_session_local()
        # 确保请求结束后关闭会话。
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
    # 返回测试客户端。
    yield client
    # 清理依赖覆盖避免影响其他测试。
    app.dependency_overrides.clear()


# 验证健康检查成功响应使用统一信封。
def test_health_success_uses_response_envelope(test_client):
    # 请求健康检查接口。
    response = test_client.get("/health")

    # 断言请求成功。
    assert response.status_code == 200
    # 断言响应使用成功信封。
    assert response.json() == {"code": 0, "message": "success", "data": {"status": "ok", "service": "fastapi-scaffold"}}


# 验证重复注册的领域异常使用统一错误信封。
def test_domain_error_uses_response_envelope(test_client):
    # 定义注册请求数据。
    payload = {"username": "alice", "email": "alice@example.com", "password": "secret-password"}
    # 创建初始用户。
    test_client.post("/auth/register", json=payload)
    # 发送重复注册请求。
    response = test_client.post("/auth/register", json=payload)

    # 断言冲突状态码未改变。
    assert response.status_code == 409
    # 断言领域异常使用统一错误信封。
    assert response.json() == {"code": 409, "message": "用户名或邮箱已存在", "data": None}


# 验证请求校验错误使用统一错误信封。
def test_validation_error_uses_response_envelope(test_client):
    # 发送缺失必填字段的注册请求。
    response = test_client.post("/auth/register", json={})

    # 断言请求校验状态码未改变。
    assert response.status_code == 422
    # 断言请求校验使用统一错误信封。
    assert response.json() == {"code": 422, "message": "请求参数校验失败", "data": None}


# 验证框架路由不存在错误使用统一错误信封。
def test_missing_route_uses_response_envelope(test_client):
    # 请求不存在的接口。
    response = test_client.get("/missing")

    # 断言路由不存在状态码未改变。
    assert response.status_code == 404
    # 断言框架异常使用统一错误信封。
    assert response.json() == {"code": 404, "message": "Not Found", "data": None}
