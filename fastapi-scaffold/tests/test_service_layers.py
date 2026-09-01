# 导入 pytest 测试框架。
import pytest
# 导入 SQLAlchemy 测试引擎创建函数。
from sqlalchemy import create_engine
# 导入 SQLAlchemy 会话工厂。
from sqlalchemy.orm import sessionmaker

# 导入数据库基类。
from app.core.database import Base
# 导入认证服务。
from app.services.auth_service import AuthService
# 导入业务冲突异常。
from app.services.exceptions import ConflictError
# 导入用户注册请求模型。
from app.schemas.auth import UserRegister


# 验证认证服务拒绝重复用户名。
def test_auth_service_rejects_duplicate_username(tmp_path):
    # 创建测试专用 SQLite 引擎。
    engine = create_engine(f"sqlite:///{tmp_path / 'service.db'}")
    # 创建全部数据表。
    Base.metadata.create_all(bind=engine)
    # 创建数据库会话。
    database_session = sessionmaker(bind=engine)()
    # 创建认证服务。
    service = AuthService(database_session)
    # 注册首个用户。
    service.register(UserRegister(username="alice", email="alice@example.com", password="secret-password"))
    # 断言重复用户名触发业务冲突。
    with pytest.raises(ConflictError, match="用户名或邮箱已存在"):
        # 尝试注册重复用户名。
        service.register(UserRegister(username="alice", email="other@example.com", password="secret-password"))
