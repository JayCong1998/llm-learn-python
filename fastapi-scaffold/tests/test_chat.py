# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient
# 导入应用实例。
from app.main import app

# 验证聊天会话创建接口已注册。
def test_chat_conversation_create_route_is_registered():
    # 创建应用测试客户端。
    client = TestClient(app)
    # 发送未认证的创建会话请求。
    response = client.post("/chat/conversations", json={})
    # 断言路由存在且要求认证。
    assert response.status_code == 401
