# 导入 Pydantic 基础模型。
from pydantic import BaseModel
# 导入 Pydantic 字段约束工具。
from pydantic import Field
# 导入 Pydantic 对象属性读取配置。
from pydantic import ConfigDict


# 定义用户注册请求数据模型。
class UserRegister(BaseModel):
    # 限制用户名长度。
    username: str = Field(min_length=3, max_length=50)
    # 限制邮箱字符串长度。
    email: str = Field(min_length=3, max_length=255)
    # 限制密码最小长度。
    password: str = Field(min_length=8, max_length=128)


# 定义用户登录请求数据模型。
class UserLogin(BaseModel):
    # 限制登录用户名长度。
    username: str = Field(min_length=3, max_length=50)
    # 限制登录密码长度。
    password: str = Field(min_length=8, max_length=128)


# 定义对外暴露的用户数据模型。
class UserRead(BaseModel):
    # 启用从 ORM 对象属性读取字段。
    model_config = ConfigDict(from_attributes=True)

    # 定义用户主键字段。
    id: int
    # 定义用户名字段。
    username: str
    # 定义邮箱字段。
    email: str
    # 定义角色字段。
    role: str


# 定义登录成功后的令牌响应模型。
class TokenResponse(BaseModel):
    # 定义 JWT 访问令牌字段。
    access_token: str
    # 定义认证方案类型字段。
    token_type: str
