# API 统一响应与全局异常处理实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 为非流式 JSON API 统一成功/失败响应信封，并在应用级集中转换异常。

**架构：** `app/core/api_response.py` 定义响应模型、成功响应路由与异常处理函数；`main.py` 安装统一路由类和 handler。领域异常带有 HTTP 状态与应用码，路由和依赖仅抛出领域异常。响应路由跳过显式响应对象和 204。

**技术栈：** FastAPI、Starlette、Pydantic、pytest、httpx TestClient。

---

### 任务 1：定义统一响应及全局异常处理的失败测试

**文件：**
- 创建：`tests/test_api_response.py`
- 修改：`tests/test_auth.py`
- 修改：`tests/test_health.py`

- [ ] **步骤 1：编写失败的测试**

```python
def test_health_is_wrapped(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"code": 0, "message": "success", "data": {"status": "ok", "service": "fastapi-scaffold"}}

def test_validation_error_uses_error_envelope(test_client):
    response = test_client.post("/auth/register", json={})
    assert response.status_code == 422
    assert response.json()["data"] is None
    assert response.json()["code"] == 422

def test_missing_route_uses_error_envelope(test_client):
    response = test_client.get("/missing")
    assert response.status_code == 404
    assert response.json() == {"code": 404, "message": "Not Found", "data": None}
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m pytest tests/test_api_response.py -q`

预期：FAIL；现有接口返回裸业务数据或 FastAPI 默认 `detail` 结构。

### 任务 2：集中异常映射并为非流式 JSON 响应增加信封

**文件：**
- 创建：`app/core/api_response.py`
- 修改：`app/main.py`
- 修改：`app/services/exceptions.py`
- 修改：`app/core/dependencies.py`
- 修改：`app/api/auth.py`
- 修改：`app/api/chat.py`

- [ ] **步骤 1：实现领域异常元数据和应用级处理函数**

```python
class DomainError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = status.HTTP_400_BAD_REQUEST

async def domain_error_handler(_: Request, error: DomainError) -> JSONResponse:
    return error_response(error.status_code, error.error_code, str(error))
```

- [ ] **步骤 2：实现成功响应路由**

```python
class EnvelopeRoute(APIRoute):
    def get_route_handler(self):
        original_handler = super().get_route_handler()
        async def wrapped(request: Request) -> Response:
            response = await original_handler(request)
            if response.status_code == status.HTTP_204_NO_CONTENT or isinstance(response, StreamingResponse):
                return response
            return JSONResponse(status_code=response.status_code, content=success_payload(json.loads(response.body)))
        return wrapped
```

- [ ] **步骤 3：安装 handler，移除路由和依赖的 `HTTPException` 转换**

```python
app = FastAPI(title=settings.app_name)
app.router.route_class = EnvelopeRoute
app.add_exception_handler(DomainError, domain_error_handler)
```

认证依赖改为抛 `AuthenticationError`；权限依赖改为抛 `AuthorizationError`；认证和聊天路由直接调用服务。

- [ ] **步骤 4：运行任务 1 测试验证通过**

运行：`python -m pytest tests/test_api_response.py -q`

预期：PASS。

### 任务 3：补全回归测试并验证完整套件

**文件：**
- 修改：`tests/test_auth.py`
- 修改：`tests/test_chat.py`
- 修改：`tests/test_health.py`
- 修改：`tests/test_api_response.py`

- [ ] **步骤 1：断言认证成功、冲突、认证失败和权限失败都遵循响应信封**

```python
assert response.json()["data"]["username"] == "alice"
assert response.json()["code"] == 409
assert response.json()["data"] is None
```

- [ ] **步骤 2：断言未认证聊天请求与 204 响应保持正确协议**

```python
assert response.status_code == 401
assert response.json()["code"] == 401
assert delete_response.status_code == 204
assert delete_response.content == b""
```

- [ ] **步骤 3：运行完整测试套件**

运行：`python -m pytest -q`

预期：PASS。
