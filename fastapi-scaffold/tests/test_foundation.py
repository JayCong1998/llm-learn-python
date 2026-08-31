# 导入日期时间类型。
from datetime import timedelta

# 导入测试断言工具。
import pytest

# 导入 SQLAlchemy 引擎创建函数。
from sqlalchemy import create_engine
# 导入数据库完整性异常类型。
from sqlalchemy.exc import IntegrityError
# 导入 SQLAlchemy 表检查工具。
from sqlalchemy import inspect
# 导入 SQLAlchemy 会话工厂。
from sqlalchemy.orm import sessionmaker

# 导入数据库基类。
from app.core.database import Base
# 导入令牌创建函数。
from app.core.security import create_access_token
# 导入令牌解析函数。
from app.core.security import decode_access_token
# 导入密码哈希函数。
from app.core.security import hash_password
# 导入密码校验函数。
from app.core.security import verify_password
# 导入品牌模型以注册映射表。
from app.models.brand import Brand
# 导入车型模型以注册映射表。
from app.models.car_model import CarModel
# 导入用户模型以注册映射表。
from app.models.user import User


# 验证模型会创建车辆管理所需的数据表。
def test_models_create_expected_tables(tmp_path):
    # 创建测试专用 SQLite 引擎。
    engine = create_engine(f"sqlite:///{tmp_path / 'models.db'}")
    # 创建全部模型对应的数据表。
    Base.metadata.create_all(bind=engine)
    # 读取已创建的表名集合。
    table_names = set(inspect(engine).get_table_names())

    # 断言用户表已创建。
    assert "users" in table_names
    # 断言品牌表已创建。
    assert "brands" in table_names
    # 断言车型表已创建。
    assert "car_models" in table_names


# 验证品牌与车型模型保存外键关联。
def test_car_model_belongs_to_brand(tmp_path):
    # 创建测试专用 SQLite 引擎。
    engine = create_engine(f"sqlite:///{tmp_path / 'relationships.db'}")
    # 创建全部模型对应的数据表。
    Base.metadata.create_all(bind=engine)
    # 创建绑定测试引擎的会话工厂。
    session_factory = sessionmaker(bind=engine)
    # 创建数据库会话。
    session = session_factory()
    # 创建待关联的品牌实体。
    brand = Brand(name="Tesla", country="United States", description="EV maker")
    # 保存品牌实体以生成主键。
    session.add(brand)
    # 写入品牌实体。
    session.commit()
    # 创建关联该品牌的车型实体。
    car_model = CarModel(name="Model 3", year=2026, price=299999.00, brand_id=brand.id)
    # 保存车型实体。
    session.add(car_model)
    # 写入车型实体。
    session.commit()
    # 刷新品牌实体以加载关联集合。
    session.refresh(brand)

    # 断言车型可关联回所属品牌。
    assert car_model.brand.name == "Tesla"
    # 断言品牌可获取关联车型。
    assert brand.car_models[0].name == "Model 3"
    # 关闭数据库会话。
    session.close()


# 验证 SQLite 会拒绝写入不存在品牌的车型。
def test_sqlite_rejects_car_model_with_unknown_brand(tmp_path):
    # 创建测试专用 SQLite 引擎。
    engine = create_engine(f"sqlite:///{tmp_path / 'foreign-key.db'}")
    # 创建全部模型对应的数据表。
    Base.metadata.create_all(bind=engine)
    # 创建绑定测试引擎的会话工厂。
    session_factory = sessionmaker(bind=engine)
    # 创建数据库会话。
    session = session_factory()
    # 创建引用不存在品牌的车型实体。
    car_model = CarModel(name="Unknown", year=2026, price=1.00, brand_id=999)
    # 保存非法车型实体。
    session.add(car_model)

    # 断言提交非法外键会触发完整性异常。
    with pytest.raises(IntegrityError):
        # 提交事务以触发数据库约束校验。
        session.commit()
    # 回滚失败事务以恢复会话状态。
    session.rollback()
    # 关闭数据库会话。
    session.close()


# 验证密码只可通过校验函数验证而非明文比较。
def test_password_hash_can_be_verified():
    # 生成测试密码的哈希值。
    password_hash = hash_password("correct-password")

    # 断言哈希值不等于原始密码。
    assert password_hash != "correct-password"
    # 断言正确密码可以通过校验。
    assert verify_password("correct-password", password_hash) is True
    # 断言错误密码无法通过校验。
    assert verify_password("incorrect-password", password_hash) is False


# 验证访问令牌可恢复用户身份与角色。
def test_access_token_contains_subject_and_role():
    # 创建包含用户身份和角色的短期令牌。
    token = create_access_token({"sub": "alice", "role": "admin"}, timedelta(minutes=5))
    # 解析访问令牌中的声明。
    payload = decode_access_token(token)

    # 断言令牌包含用户名主体。
    assert payload["sub"] == "alice"
    # 断言令牌包含角色信息。
    assert payload["role"] == "admin"
