# 导入管理员创建模块以便替换数据库会话工厂。
from scripts import create_admin
# 导入 pytest 测试框架。
import pytest
# 导入 SQLAlchemy 测试引擎创建函数。
from sqlalchemy import create_engine
# 导入 SQLAlchemy 会话工厂。
from sqlalchemy.orm import sessionmaker
# 导入 SQLAlchemy 单连接池实现。
from sqlalchemy.pool import StaticPool
# 导入 ORM 基类以创建测试表。
from app.core.database import Base
# 导入用户模型用于验证管理员数据。
from app.models.user import User


# 创建跨线程共享单连接的测试内存数据库引擎。
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
# 创建测试数据库会话工厂。
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 为每个测试创建独立的数据库会话。
@pytest.fixture
def test_database_session():
    # 删除上一个测试遗留的数据表。
    Base.metadata.drop_all(bind=engine)
    # 创建当前测试所需的数据表。
    Base.metadata.create_all(bind=engine)
    # 创建测试数据库会话。
    database_session = TestingSessionLocal()
    # 向测试提供数据库会话。
    yield database_session
    # 关闭数据库会话释放资源。
    database_session.close()


# 验证脚本会从环境变量创建管理员且可重复执行。
def test_create_admin_is_idempotent_and_reads_environment(monkeypatch, test_database_session):
    # 写入管理员用户名环境变量。
    monkeypatch.setenv("ADMIN_USERNAME", "root")
    # 写入管理员邮箱环境变量。
    monkeypatch.setenv("ADMIN_EMAIL", "root@example.com")
    # 写入管理员密码环境变量。
    monkeypatch.setenv("ADMIN_PASSWORD", "safe-password")
    # 让脚本使用测试数据库会话。
    monkeypatch.setattr(create_admin, "SessionLocal", lambda: test_database_session)

    # 首次执行应创建管理员。
    assert create_admin.create_admin_from_environment() is True
    # 再次执行不应创建重复管理员。
    assert create_admin.create_admin_from_environment() is False
    # 按用户名读取创建的用户。
    user = test_database_session.query(User).filter_by(username="root").one()

    # 断言用户拥有管理员角色。
    assert user.role == "admin"
    # 断言用户邮箱来自环境变量。
    assert user.email == "root@example.com"
