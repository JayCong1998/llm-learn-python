"""删除汽车品牌和车型表。"""

# 导入 Alembic 迁移操作工具。
from alembic import op
# 导入 SQLAlchemy 类型定义。
import sqlalchemy as sa

# 定义本迁移的唯一版本标识。
revision = "20260901_0003"
# 定义本迁移依赖 LLM 对话持久化结构。
down_revision = "20260901_0002"
# 定义分支标签为空。
branch_labels = None
# 定义依赖版本为空。
depends_on = None

# 删除汽车业务表。
def upgrade() -> None:
    # 删除车型品牌外键索引。
    op.drop_index("ix_car_models_brand_id", table_name="car_models")
    # 删除车型表。
    op.drop_table("car_models")
    # 删除品牌名称索引。
    op.drop_index("ix_brands_name", table_name="brands")
    # 删除品牌表。
    op.drop_table("brands")

# 恢复汽车业务表。
def downgrade() -> None:
    # 创建品牌表。
    op.create_table("brands", sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(length=100), nullable=False), sa.Column("country", sa.String(length=100), nullable=False), sa.Column("description", sa.Text(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("name"))
    # 创建品牌名称索引。
    op.create_index("ix_brands_name", "brands", ["name"], unique=False)
    # 创建车型表。
    op.create_table("car_models", sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(length=100), nullable=False), sa.Column("year", sa.Integer(), nullable=False), sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False), sa.Column("brand_id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="RESTRICT"), sa.PrimaryKeyConstraint("id"))
    # 创建车型品牌外键索引。
    op.create_index("ix_car_models_brand_id", "car_models", ["brand_id"], unique=False)
