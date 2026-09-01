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
# 导入密码哈希函数。
from app.core.security import hash_password
# 导入应用实例。
from app.main import app
# 导入品牌模型以注册品牌表。
from app.models.brand import Brand
# 导入车型模型以注册车型表。
from app.models.car_model import CarModel
# 导入用户模型以注册用户表。
from app.models.user import User


# 创建跨线程共享单连接的测试内存数据库引擎。
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
# 创建测试数据库的会话工厂。
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 为每个测试重建数据表并提供 HTTP 客户端。
@pytest.fixture
# 定义车型接口的测试客户端夹具。
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


# 创建管理员并返回其认证请求头。
def create_admin_headers(test_client):
    # 创建独立数据库会话以写入管理员。
    database_session = TestingSessionLocal()
    # 创建拥有管理员角色的测试用户。
    admin = User(username="admin", email="admin@example.com", password_hash=hash_password("secret-password"), role="admin")
    # 将管理员加入数据库会话。
    database_session.add(admin)
    # 提交管理员记录。
    database_session.commit()
    # 关闭数据库会话。
    database_session.close()
    # 使用管理员账号请求访问令牌。
    response = test_client.post("/auth/login", json={"username": "admin", "password": "secret-password"})
    # 返回携带访问令牌的认证头。
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


# 创建品牌并返回其主键。
def create_brand(test_client, headers, name="Tesla"):
    # 发送创建品牌请求。
    response = test_client.post("/brands", headers=headers, json={"name": name, "country": "美国"})
    # 返回创建品牌的主键。
    return response.json()["id"]


# 验证管理员可完成车型创建、更新和删除。
def test_admin_can_create_update_and_delete_car_model(test_client):
    # 获取管理员认证请求头。
    headers = create_admin_headers(test_client)
    # 创建车型所属品牌。
    brand_id = create_brand(test_client, headers)
    # 创建车型记录。
    create_response = test_client.post("/car-models", headers=headers, json={"name": "Model 3", "year": 2025, "price": "259900.00", "brand_id": brand_id})
    # 读取新建车型主键。
    car_model_id = create_response.json()["id"]
    # 更新车型记录。
    update_response = test_client.put(f"/car-models/{car_model_id}", headers=headers, json={"name": "Model 3 焕新版", "year": 2026, "price": "269900.00", "brand_id": brand_id})
    # 删除车型记录。
    delete_response = test_client.delete(f"/car-models/{car_model_id}", headers=headers)

    # 断言车型创建成功。
    assert create_response.status_code == 201
    # 断言车型关联的品牌正确。
    assert create_response.json()["brand_id"] == brand_id
    # 断言车型更新成功。
    assert update_response.status_code == 200
    # 断言更新后的车型名称正确。
    assert update_response.json()["name"] == "Model 3 焕新版"
    # 断言车型删除成功。
    assert delete_response.status_code == 204
    # 断言被删除车型不再存在。
    assert test_client.get(f"/car-models/{car_model_id}", headers=headers).status_code == 404


# 验证车型列表拒绝匿名访问并支持登录后的过滤和分页。
def test_login_is_required_to_filter_and_paginate_car_models(test_client):
    # 获取管理员认证请求头。
    headers = create_admin_headers(test_client)
    # 创建第一品牌。
    tesla_id = create_brand(test_client, headers, "Tesla")
    # 创建第二品牌。
    byd_id = create_brand(test_client, headers, "BYD")
    # 创建第一条特斯拉车型。
    test_client.post("/car-models", headers=headers, json={"name": "Model 3", "year": 2025, "price": "259900.00", "brand_id": tesla_id})
    # 创建第二条特斯拉车型。
    test_client.post("/car-models", headers=headers, json={"name": "Model Y", "year": 2025, "price": "263500.00", "brand_id": tesla_id})
    # 创建比亚迪车型。
    test_client.post("/car-models", headers=headers, json={"name": "海豹", "year": 2025, "price": "179800.00", "brand_id": byd_id})
    # 匿名按品牌过滤并分页查询车型。
    anonymous_response = test_client.get(f"/car-models?brand_id={tesla_id}&limit=1&offset=1")
    # 已登录管理员按品牌过滤并分页查询车型。
    response = test_client.get(f"/car-models?brand_id={tesla_id}&limit=1&offset=1", headers=headers)

    # 断言匿名查询被拒绝。
    assert anonymous_response.status_code == 401
    # 断言已登录查询成功。
    assert response.status_code == 200
    # 断言分页仅返回一条数据。
    assert len(response.json()) == 1
    # 断言过滤结果属于指定品牌。
    assert response.json()[0]["brand_id"] == tesla_id
    # 断言偏移后的车型正确。
    assert response.json()[0]["name"] == "Model Y"


# 验证不存在的品牌不能用于创建或更新车型。
def test_car_model_rejects_missing_brand(test_client):
    # 获取管理员认证请求头。
    headers = create_admin_headers(test_client)
    # 使用不存在的品牌创建车型。
    response = test_client.post("/car-models", headers=headers, json={"name": "不存在品牌车型", "year": 2025, "price": "100000.00", "brand_id": 999})

    # 断言不存在品牌返回未找到。
    assert response.status_code == 404


# 验证普通用户不能写入车型数据。
def test_regular_user_cannot_write_car_model(test_client):
    # 获取管理员认证请求头以准备品牌。
    admin_headers = create_admin_headers(test_client)
    # 创建供写入请求使用的品牌。
    brand_id = create_brand(test_client, admin_headers)
    # 注册普通用户。
    test_client.post("/auth/register", json={"username": "alice", "email": "alice@example.com", "password": "secret-password"})
    # 使用普通用户账号登录。
    login_response = test_client.post("/auth/login", json={"username": "alice", "password": "secret-password"})
    # 读取普通用户访问令牌。
    token = login_response.json()["access_token"]
    # 使用普通用户令牌创建车型。
    response = test_client.post("/car-models", headers={"Authorization": f"Bearer {token}"}, json={"name": "Model 3", "year": 2025, "price": "259900.00", "brand_id": brand_id})

    # 断言普通用户被禁止写入。
    assert response.status_code == 403


# 验证存在关联车型时管理员不能删除品牌。
def test_admin_cannot_delete_brand_with_car_models(test_client):
    # 获取管理员认证请求头。
    headers = create_admin_headers(test_client)
    # 创建待删除品牌。
    brand_id = create_brand(test_client, headers)
    # 创建关联到该品牌的车型。
    test_client.post("/car-models", headers=headers, json={"name": "Model 3", "year": 2025, "price": "259900.00", "brand_id": brand_id})
    # 尝试删除仍有关联车型的品牌。
    response = test_client.delete(f"/brands/{brand_id}", headers=headers)

    # 断言业务规则拒绝该删除操作。
    assert response.status_code == 409
