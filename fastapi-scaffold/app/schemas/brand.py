# 导入 Pydantic 基础模型。
from pydantic import BaseModel
# 导入 Pydantic 对象属性读取配置。
from pydantic import ConfigDict
# 导入 Pydantic 字段约束工具。
from pydantic import Field


# 定义创建品牌的请求模型。
class BrandCreate(BaseModel):
    # 限制品牌名称长度。
    name: str = Field(min_length=1, max_length=100)
    # 限制国家名称长度。
    country: str = Field(min_length=1, max_length=100)
    # 限制可选描述长度。
    description: str | None = Field(default=None, max_length=2000)


# 定义更新品牌的请求模型。
class BrandUpdate(BaseModel):
    # 限制品牌名称长度。
    name: str = Field(min_length=1, max_length=100)
    # 限制国家名称长度。
    country: str = Field(min_length=1, max_length=100)
    # 限制可选描述长度。
    description: str | None = Field(default=None, max_length=2000)


# 定义对外返回的品牌数据模型。
class BrandRead(BaseModel):
    # 启用从 ORM 对象属性读取字段。
    model_config = ConfigDict(from_attributes=True)

    # 定义品牌主键字段。
    id: int
    # 定义品牌名称字段。
    name: str
    # 定义品牌国家字段。
    country: str
    # 定义可选品牌描述字段。
    description: str | None
