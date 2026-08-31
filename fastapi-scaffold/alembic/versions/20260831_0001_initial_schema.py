"""创建用户、汽车品牌与车型初始表。"""

# 导入 Alembic 迁移操作工具。
from alembic import op
# 导入 SQLAlchemy 类型定义。
import sqlalchemy as sa

# 定义本迁移的唯一版本标识。
revision = "20260831_0001"
# 定义初始迁移没有前置版本。
down_revision = None
# 定义分支标签为空。
branch_labels = None
# 定义依赖版本为空。
depends_on = None


# 创建项目所需的初始数据表。
def upgrade() -> None:
    # 创建用户数据表。
    op.create_table("users", sa.Column("id", sa.Integer(), nullable=False), sa.Column("username", sa.String(length=50), nullable=False), sa.Column("email", sa.String(length=255), nullable=False), sa.Column("password_hash", sa.String(length=255), nullable=False), sa.Column("role", sa.String(length=20), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("email"), sa.UniqueConstraint("username"))
    # 创建用户名索引。
    op.create_index("ix_users_username", "users", ["username"], unique=False)
    # 创建邮箱索引。
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    # 创建汽车品牌数据表。
    op.create_table("brands", sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(length=100), nullable=False), sa.Column("country", sa.String(length=100), nullable=False), sa.Column("description", sa.Text(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("name"))
    # 创建品牌名称索引。
    op.create_index("ix_brands_name", "brands", ["name"], unique=False)
    # 创建车型数据表。
    op.create_table("car_models", sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(length=100), nullable=False), sa.Column("year", sa.Integer(), nullable=False), sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False), sa.Column("brand_id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="RESTRICT"), sa.PrimaryKeyConstraint("id"))
    # 创建车型品牌外键索引。
    op.create_index("ix_car_models_brand_id", "car_models", ["brand_id"], unique=False)


# 删除项目初始数据表。
def downgrade() -> None:
    # 删除车型品牌外键索引。
    op.drop_index("ix_car_models_brand_id", table_name="car_models")
    # 删除车型数据表。
    op.drop_table("car_models")
    # 删除品牌名称索引。
    op.drop_index("ix_brands_name", table_name="brands")
    # 删除汽车品牌数据表。
    op.drop_table("brands")
    # 删除邮箱索引。
    op.drop_index("ix_users_email", table_name="users")
    # 删除用户名索引。
    op.drop_index("ix_users_username", table_name="users")
    # 删除用户数据表。
    op.drop_table("users")
