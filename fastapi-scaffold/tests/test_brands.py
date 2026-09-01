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
# 导入车型模型以解析品牌关联。
from app.models.car_model import CarModel
# 导入用户模型以注册用户表。
from app.models.user import User


# 创建跨线程共享单连接的测试内存数据库引擎。
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
# 创建测试数据库的会话工厂。
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 为每个测试重建数据表并提供 HTTP 客户端。
@pytest.fixture
# 定义品牌接口的测试客户端夹具。
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
    # 读取登录响应中的访问令牌。
    token = response.json()["access_token"]
    # 返回 Bearer 认证头。
    return {"Authorization": f"Bearer {token}"}


# 验证品牌读取接口拒绝匿名访问并允许已登录用户读取。
def test_login_is_required_to_list_and_get_brand_details(test_client):
    # 创建测试数据库会话。
    database_session = TestingSessionLocal()
    # 创建供公开查询的品牌记录。
    brand = Brand(name="Tesla", country="美国", description="电动汽车品牌")
    # 将品牌加入数据库会话。
    database_session.add(brand)
    # 提交品牌记录。
    database_session.commit()
    # 刷新品牌以获得主键。
    database_session.refresh(brand)
    # 保存品牌主键供会话关闭后使用。
    brand_id = brand.id
    # 关闭数据库会话。
    database_session.close()
    # 匿名请求品牌列表。
    anonymous_list_response = test_client.get("/brands")
    # 匿名请求品牌详情。
    anonymous_detail_response = test_client.get(f"/brands/{brand_id}")
    # 注册普通用户。
    test_client.post("/auth/register", json={"username": "reader", "email": "reader@example.com", "password": "secret-password"})
    # 使用普通用户账号登录。
    login_response = test_client.post("/auth/login", json={"username": "reader", "password": "secret-password"})
    # 组装普通用户认证请求头。
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    # 已登录用户请求品牌列表。
    list_response = test_client.get("/brands", headers=headers)
    # 已登录用户请求品牌详情。
    detail_response = test_client.get(f"/brands/{brand_id}", headers=headers)

    # 断言匿名品牌列表请求被拒绝。
    assert anonymous_list_response.status_code == 401
    # 断言匿名品牌详情请求被拒绝。
    assert anonymous_detail_response.status_code == 401
    # 断言已登录用户品牌列表请求成功。
    assert list_response.status_code == 200
    # 断言品牌列表返回已创建品牌。
    assert list_response.json()[0]["name"] == "Tesla"
    # 断言已登录用户品牌详情请求成功。
    assert detail_response.status_code == 200
    # 断言品牌详情返回正确国家。
    assert detail_response.json()["country"] == "美国"


# 验证管理员可完成品牌创建、更新和删除。
def test_admin_can_create_update_and_delete_brand(test_client):
    # 获取管理员认证请求头。
    headers = create_admin_headers(test_client)
    # 创建品牌记录。
    create_response = test_client.post("/brands", headers=headers, json={"name": "BYD", "country": "中国", "description": "新能源"})
    # 读取新建品牌主键。
    brand_id = create_response.json()["id"]
    # 更新品牌记录。
    update_response = test_client.put(f"/brands/{brand_id}", headers=headers, json={"name": "比亚迪", "country": "中国", "description": "更新描述"})
    # 删除品牌记录。
    delete_response = test_client.delete(f"/brands/{brand_id}", headers=headers)

    # 断言品牌创建成功。
    assert create_response.status_code == 201
    # 断言品牌更新成功。
    assert update_response.status_code == 200
    # 断言更新后的名称正确。
    assert update_response.json()["name"] == "比亚迪"
    # 断言品牌删除成功。
    assert delete_response.status_code == 204
    # 断言被删除品牌不再存在。
    assert test_client.get(f"/brands/{brand_id}", headers=headers).status_code == 404


# 验证普通用户不能修改品牌。
def test_regular_user_cannot_write_brand(test_client):
    # 注册普通用户。
    test_client.post("/auth/register", json={"username": "alice", "email": "alice@example.com", "password": "secret-password"})
    # 获取普通用户访问令牌。
    login_response = test_client.post("/auth/login", json={"username": "alice", "password": "secret-password"})
    # 读取普通用户访问令牌。
    token = login_response.json()["access_token"]
    # 使用普通用户令牌创建品牌。
    response = test_client.post("/brands", headers={"Authorization": f"Bearer {token}"}, json={"name": "BMW", "country": "德国"})

    # 断言普通用户被禁止写入。
    assert response.status_code == 403


# 验证重复品牌和不存在资源返回正确状态码。
def test_brand_reports_conflict_and_not_found(test_client):
    # 获取管理员认证请求头。
    headers = create_admin_headers(test_client)
    # 定义首次创建品牌的请求数据。
    payload = {"name": "Audi", "country": "德国"}
    # 创建首次品牌记录。
    test_client.post("/brands", headers=headers, json=payload)
    # 使用相同名称重复创建品牌。
    conflict_response = test_client.post("/brands", headers=headers, json=payload)
    # 请求不存在的品牌详情。
    missing_response = test_client.get("/brands/999", headers=headers)

    # 断言重复品牌返回冲突状态。
    assert conflict_response.status_code == 409
    # 断言不存在品牌返回未找到状态。
    assert missing_response.status_code == 404
