# FastAPI 分层分包迁移 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 FastAPI 脚手架迁移至薄路由、service 业务编排和 repository 数据访问的分层结构，同时保持全部对外接口行为不变。

**Architecture:** 新增 `repositories` 封装 SQLAlchemy 查询和实体写入；新增 `services` 承担业务校验、事务提交/回滚和领域异常。API 仅解析 HTTP、调用服务，并把领域异常转换为既有 HTTP 响应。

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.x, Pydantic 2, PyJWT, pytest, HTTPX.

---

### Task 1: 建立领域异常和 repository 层

**Files:**
- Create: `fastapi-scaffold/app/services/__init__.py`
- Create: `fastapi-scaffold/app/services/exceptions.py`
- Create: `fastapi-scaffold/app/repositories/__init__.py`
- Create: `fastapi-scaffold/app/repositories/user_repository.py`
- Create: `fastapi-scaffold/app/repositories/brand_repository.py`
- Create: `fastapi-scaffold/app/repositories/car_model_repository.py`
- Test: `fastapi-scaffold/tests/test_repositories.py`

- [ ] **Step 1: 写入 repository 模块的失败测试**

```python
from app.repositories.brand_repository import BrandRepository
from app.repositories.car_model_repository import CarModelRepository
from app.repositories.user_repository import UserRepository

def test_repositories_return_no_entity_for_unknown_values(session):
    assert UserRepository(session).find_by_username("alice") is None
    assert BrandRepository(session).get(999) is None
    assert CarModelRepository(session).list(None, 20, 0) == []
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_repositories.py -v`

Expected: FAIL with `ModuleNotFoundError` for `app.repositories`.

- [ ] **Step 3: 实现异常和三个 repository**

```python
class DomainError(Exception):
    pass

class ConflictError(DomainError):
    pass

class NotFoundError(DomainError):
    pass

class AuthenticationError(DomainError):
    pass

class UserRepository:
    def find_by_username(self, username: str) -> User | None: ...
    def find_by_username_or_email(self, username: str, email: str) -> User | None: ...
    def add(self, user: User) -> None: ...

class BrandRepository:
    def get(self, brand_id: int) -> Brand | None: ...
    def list(self) -> list[Brand]: ...
    def find_by_name(self, name: str, exclude_id: int | None = None) -> Brand | None: ...
    def add(self, brand: Brand) -> None: ...
    def delete(self, brand: Brand) -> None: ...
    def has_car_models(self, brand_id: int) -> bool: ...

class CarModelRepository:
    def get(self, car_model_id: int) -> CarModel | None: ...
    def list(self, brand_id: int | None, limit: int, offset: int) -> list[CarModel]: ...
    def add(self, car_model: CarModel) -> None: ...
    def delete(self, car_model: CarModel) -> None: ...
```

使用 `select` 实现查询和筛选分页；repository 只读写 session，绝不 `commit()`。每个新增 Python 有效代码行前加中文独立行注释。

- [ ] **Step 4: 运行 repository 测试确认通过**

Run: `python -m pytest tests/test_repositories.py -v`

Expected: PASS.

- [ ] **Step 5: 提交**

```powershell
git add fastapi-scaffold/app/repositories fastapi-scaffold/app/services fastapi-scaffold/tests/test_repositories.py
git commit -m "refactor: add data repositories"
```

### Task 2: 迁移认证业务至 auth service

**Files:**
- Create: `fastapi-scaffold/app/services/auth_service.py`
- Modify: `fastapi-scaffold/app/api/auth.py`
- Create: `fastapi-scaffold/tests/test_auth_service.py`
- Modify: `fastapi-scaffold/tests/test_auth.py`

- [ ] **Step 1: 写服务失败测试**

```python
def test_auth_service_rejects_duplicate_user(session):
    service = AuthService(session)
    service.register(UserRegister(username="alice", email="alice@example.com", password="secret-password"))
    with pytest.raises(ConflictError, match="用户名或邮箱已存在"):
        service.register(UserRegister(username="alice", email="other@example.com", password="secret-password"))

def test_auth_service_rejects_wrong_password(session):
    with pytest.raises(AuthenticationError, match="用户名或密码错误"):
        AuthService(session).login(UserLogin(username="missing", password="secret-password"))
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_auth_service.py -v`

Expected: FAIL with missing `AuthService`.

- [ ] **Step 3: 实现认证服务和薄路由**

```python
class AuthService:
    def register(self, payload: UserRegister) -> User:
        if self.user_repository.find_by_username_or_email(payload.username, payload.email):
            raise ConflictError("用户名或邮箱已存在")
        user = User(username=payload.username, email=payload.email, password_hash=hash_password(payload.password), role="user")
        self.user_repository.add(user)
        self.database_session.commit()
        self.database_session.refresh(user)
        return user

    def login(self, payload: UserLogin) -> TokenResponse:
        user = self.user_repository.find_by_username(payload.username)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise AuthenticationError("用户名或密码错误")
        return TokenResponse(access_token=create_access_token({"sub": user.username, "role": user.role}), token_type="bearer")
```

路由只创建服务、调用服务，且映射 `ConflictError → 409`、`AuthenticationError → 401`；保留管理员探针。

- [ ] **Step 4: 回归认证测试**

Run: `python -m pytest tests/test_auth_service.py tests/test_auth.py -v`

Expected: PASS.

- [ ] **Step 5: 提交**

```powershell
git add fastapi-scaffold/app/services/auth_service.py fastapi-scaffold/app/api/auth.py fastapi-scaffold/tests
git commit -m "refactor: move authentication logic to service"
```

### Task 3: 迁移品牌和车型业务至 services

**Files:**
- Create: `fastapi-scaffold/app/services/brand_service.py`
- Create: `fastapi-scaffold/app/services/car_model_service.py`
- Modify: `fastapi-scaffold/app/api/brands.py`
- Modify: `fastapi-scaffold/app/api/car_models.py`
- Create: `fastapi-scaffold/tests/test_brand_service.py`
- Create: `fastapi-scaffold/tests/test_car_model_service.py`
- Modify: `fastapi-scaffold/tests/test_brands.py`
- Modify: `fastapi-scaffold/tests/test_car_models.py`

- [ ] **Step 1: 写服务失败测试**

```python
def test_brand_service_rejects_duplicate_name(session):
    service = BrandService(session)
    service.create(BrandCreate(name="Tesla", country="US", description=None))
    with pytest.raises(ConflictError, match="品牌名称已存在"):
        service.create(BrandCreate(name="Tesla", country="US", description=None))

def test_car_model_service_rejects_unknown_brand(session):
    with pytest.raises(NotFoundError, match="品牌不存在"):
        CarModelService(session).create(CarModelCreate(name="Model 3", year=2026, price=299999, brand_id=999))
```

- [ ] **Step 2: 运行服务测试确认失败**

Run: `python -m pytest tests/test_brand_service.py tests/test_car_model_service.py -v`

Expected: FAIL with missing service modules.

- [ ] **Step 3: 实现服务与 API 异常映射**

```python
class BrandService:
    def get_or_raise(self, brand_id: int) -> Brand: ...
    def list(self) -> list[Brand]: ...
    def create(self, payload: BrandCreate) -> Brand: ...
    def update(self, brand_id: int, payload: BrandUpdate) -> Brand: ...
    def delete(self, brand_id: int) -> None: ...

class CarModelService:
    def get_or_raise(self, car_model_id: int) -> CarModel: ...
    def require_brand(self, brand_id: int) -> Brand: ...
    def list(self, brand_id: int | None, limit: int, offset: int) -> list[CarModel]: ...
    def create(self, payload: CarModelCreate) -> CarModel: ...
    def update(self, car_model_id: int, payload: CarModelUpdate) -> CarModel: ...
    def delete(self, car_model_id: int) -> None: ...
```

服务把不存在资源转换为 `NotFoundError`，把重复名称和关联车型删除转换为 `ConflictError`，成功写入后提交刷新，失败写入时回滚；API 映射 404 与 409，保留全部 URL、依赖和 response model。

- [ ] **Step 4: 回归资源测试**

Run: `python -m pytest tests/test_brand_service.py tests/test_car_model_service.py tests/test_brands.py tests/test_car_models.py -v`

Expected: PASS.

- [ ] **Step 5: 提交**

```powershell
git add fastapi-scaffold/app/services fastapi-scaffold/app/api fastapi-scaffold/tests
git commit -m "refactor: move vehicle management logic to services"
```

### Task 4: 验证架构边界与完整回归

**Files:**
- Modify: `fastapi-scaffold/tests/test_foundation.py`
- Modify: `fastapi-scaffold/README.md`

- [ ] **Step 1: 写 API 边界测试**

```python
def test_api_modules_do_not_import_orm_or_sqlalchemy():
    for api_file in ("auth.py", "brands.py", "car_models.py"):
        source = (Path("app/api") / api_file).read_text(encoding="utf-8")
        assert "from sqlalchemy" not in source
        assert "from app.models" not in source
```

- [ ] **Step 2: 运行测试确认边界**

Run: `python -m pytest tests/test_foundation.py -v`

Expected: PASS after Task 3.

- [ ] **Step 3: 更新 README 架构说明**

```text
app/api：HTTP 路由与错误映射。
app/services：业务规则与事务边界。
app/repositories：SQLAlchemy 数据访问。
```

- [ ] **Step 4: 运行完整测试**

Run: `python -m pytest -q`

Expected: PASS with no failures.

- [ ] **Step 5: 提交**

```powershell
git add fastapi-scaffold/tests/test_foundation.py fastapi-scaffold/README.md
git commit -m "test: verify layered fastapi boundaries"
```

