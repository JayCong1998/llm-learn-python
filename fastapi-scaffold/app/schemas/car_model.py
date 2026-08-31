# 导入金额字段所需的十进制类型。
from decimal import Decimal

# 导入 Pydantic 基础模型。
from pydantic import BaseModel
# 导入 Pydantic 对象属性读取配置。
from pydantic import ConfigDict
# 导入 Pydantic 字段约束工具。
from pydantic import Field


# 定义创建车型的请求模型。
class CarModelCreate(BaseModel):
    # 限制车型名称长度。
    name: str = Field(min_length=1, max_length=100)
    # 限制年款为合理的正整数。
    year: int = Field(ge=1886, le=9999)
    # 限制价格为正数。
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    # 限制所属品牌主键为正整数。
    brand_id: int = Field(gt=0)


# 定义更新车型的请求模型。
class CarModelUpdate(CarModelCreate):
    # 继承创建车型所需的全部字段约束。
    pass


# 定义对外返回的车型数据模型。
class CarModelRead(BaseModel):
    # 启用从 ORM 对象属性读取字段。
    model_config = ConfigDict(from_attributes=True)

    # 定义车型主键字段。
    id: int
    # 定义车型名称字段。
    name: str
    # 定义车型年款字段。
    year: int
    # 定义车型价格字段。
    price: Decimal
    # 定义所属品牌主键字段。
    brand_id: int
