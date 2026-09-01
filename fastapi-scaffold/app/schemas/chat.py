# 导入 Pydantic 基础模型。
from pydantic import BaseModel
# 导入 Pydantic 属性读取配置。
from pydantic import ConfigDict
# 导入 Pydantic 字段约束工具。
from pydantic import Field

# 定义创建会话请求模型。
class ConversationCreate(BaseModel):
    # 定义可选会话标题。
    title: str | None = Field(default=None, max_length=255)

# 定义发送消息请求模型。
class MessageCreate(BaseModel):
    # 定义消息内容。
    content: str = Field(min_length=1)

# 定义消息响应模型。
class MessageRead(BaseModel):
    # 启用 ORM 属性读取。
    model_config = ConfigDict(from_attributes=True)
    # 定义消息主键。
    id: int
    # 定义消息角色。
    role: str
    # 定义消息内容。
    content: str

# 定义会话响应模型。
class ConversationRead(BaseModel):
    # 启用 ORM 属性读取。
    model_config = ConfigDict(from_attributes=True)
    # 定义会话主键。
    id: int
    # 定义会话标题。
    title: str | None

# 定义会话详情响应模型。
class ConversationDetail(ConversationRead):
    # 定义历史消息。
    messages: list[MessageRead]
