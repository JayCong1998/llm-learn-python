# 导入令牌过期时间计算工具。
from datetime import datetime
# 导入令牌有效期时间差类型。
from datetime import timedelta
# 导入协调世界时区对象。
from datetime import timezone

# 导入 JWT 编码与解码库。
import jwt
# 导入安全密码哈希工具。
from pwdlib import PasswordHash

# 导入应用配置。
from app.core.config import settings

# 创建推荐安全算法的密码哈希器。
password_hash = PasswordHash.recommended()
# 定义 JWT 使用的签名算法。
JWT_ALGORITHM = "HS256"


# 生成不保存明文的密码哈希值。
def hash_password(password: str) -> str:
    # 返回密码哈希器生成的安全哈希值。
    return password_hash.hash(password)


# 校验用户输入密码是否匹配已保存哈希值。
def verify_password(password: str, hashed_password: str) -> bool:
    # 返回密码哈希器的校验结果。
    return password_hash.verify(password, hashed_password)


# 根据身份声明生成带有效期的 JWT 访问令牌。
def create_access_token(data: dict[str, str], expires_delta: timedelta | None = None) -> str:
    # 复制调用方数据避免修改原始字典。
    token_data = data.copy()
    # 使用传入有效期或配置默认有效期计算过期时间。
    expires_at = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.jwt_expire_minutes))
    # 写入 JWT 标准过期声明。
    token_data["exp"] = expires_at
    # 返回使用应用密钥签名的访问令牌。
    return jwt.encode(token_data, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)


# 解码并校验 JWT 访问令牌。
def decode_access_token(token: str) -> dict[str, str]:
    # 返回通过签名和有效期验证的令牌声明。
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])
