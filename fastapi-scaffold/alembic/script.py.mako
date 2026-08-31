"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
# 导入迁移版本类型定义。
from typing import Sequence, Union

# 导入 Alembic 迁移操作工具。
from alembic import op
# 导入 SQLAlchemy 类型定义。
import sqlalchemy as sa
${imports if imports else ""}

# 定义迁移版本标识。
revision: str = ${repr(up_revision)}
# 定义前置迁移版本标识。
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
# 定义迁移分支标签。
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
# 定义迁移依赖版本标识。
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


# 定义数据库升级迁移函数。
def upgrade() -> None:
    """升级数据库结构。"""
    ${upgrades if upgrades else "pass"}


# 定义数据库降级迁移函数。
def downgrade() -> None:
    """降级数据库结构。"""
    ${downgrades if downgrades else "pass"}
