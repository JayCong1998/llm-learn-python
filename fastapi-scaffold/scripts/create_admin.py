# 导入系统环境变量读取工具。
import os

# 导入环境文件加载工具。
from dotenv import load_dotenv

# 导入数据库会话工厂。
from app.core.database import SessionLocal
# 导入密码哈希函数。
from app.core.security import hash_password
# 导入用户数据库模型。
from app.models.user import User


# 从环境变量创建管理员账户并返回是否新建。
def create_admin_from_environment() -> bool:
    # 加载当前工作目录中的环境文件配置。
    load_dotenv()
    # 读取管理员用户名配置。
    username = os.getenv("ADMIN_USERNAME")
    # 读取管理员邮箱配置。
    email = os.getenv("ADMIN_EMAIL")
    # 读取管理员密码配置。
    password = os.getenv("ADMIN_PASSWORD")
    # 拒绝缺少任一管理员配置的执行。
    if not all((username, email, password)):
        # 报告必须提供的环境变量名称。
        raise ValueError("必须设置 ADMIN_USERNAME、ADMIN_EMAIL 和 ADMIN_PASSWORD")
    # 创建数据库会话。
    database_session = SessionLocal()
    # 确保会话始终被关闭。
    try:
        # 按用户名或邮箱查询现有账户。
        existing_user = database_session.query(User).filter((User.username == username) | (User.email == email)).first()
        # 跳过已存在的账户以保持脚本可重复执行。
        if existing_user is not None:
            # 返回未新建管理员的结果。
            return False
        # 创建密码哈希后的管理员实体。
        admin_user = User(username=username, email=email, password_hash=hash_password(password), role="admin")
        # 将管理员加入当前事务。
        database_session.add(admin_user)
        # 提交管理员数据。
        database_session.commit()
        # 返回成功新建管理员的结果。
        return True
    # 在发生异常时回滚当前事务。
    except Exception:
        # 撤销未提交的数据变更。
        database_session.rollback()
        # 继续向调用方抛出原始异常。
        raise
    # 无论执行结果如何都关闭数据库会话。
    finally:
        # 释放数据库连接资源。
        database_session.close()


# 提供命令行脚本入口。
def main() -> None:
    # 执行管理员创建逻辑。
    created = create_admin_from_environment()
    # 根据执行结果输出说明信息。
    message = "管理员已创建。" if created else "管理员已存在，跳过创建。"
    # 输出脚本执行结果。
    print(message)


# 仅在直接运行脚本时执行命令行入口。
if __name__ == "__main__":
    # 调用命令行入口函数。
    main()
