# 定义业务领域异常的共同基类。
class DomainError(Exception):
    # 保持领域异常基类不定义额外成员。
    pass


# 定义业务资源冲突异常。
class ConflictError(DomainError):
    # 保持冲突异常不定义额外成员。
    pass


# 定义业务资源未找到异常。
class NotFoundError(DomainError):
    # 保持未找到异常不定义额外成员。
    pass


# 定义业务认证失败异常。
class AuthenticationError(DomainError):
    # 保持认证异常不定义额外成员。
    pass
