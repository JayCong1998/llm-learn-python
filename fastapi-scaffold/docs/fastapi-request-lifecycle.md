# FastAPI 请求生命周期：以 Spring Boot 开发者的视角理解

本文以本项目的“创建车型”接口为例，沿着一次 HTTP 请求实际经过的路径，解释 FastAPI 的路由装饰器、参数解析、依赖注入、`yield` 资源管理、响应序列化和异常处理。

如果你熟悉 Spring Boot，可以先记住这个近似关系：

| Spring Boot | FastAPI |
| --- | --- |
| `@SpringBootApplication` 创建应用 | `app = FastAPI(...)` 创建应用 |
| `@RestController` / `@RequestMapping` | `APIRouter` / `@router.get()`、`@router.post()` |
| `@RequestBody` + Bean Validation | Pydantic 请求模型参数，例如 `payload: CarModelCreate` |
| `@RequestParam` / `@PathVariable` | 普通参数及 `Query()`、`Path()` 注解 |
| IoC 容器中的 Bean 注入 | `Depends(...)` 声明的按请求依赖注入 |
| Filter / Interceptor / AOP 环绕通知 | Middleware、依赖链、`yield` 依赖 |
| `@ControllerAdvice` | `HTTPException`、异常处理器 |
| Jackson 序列化 | Pydantic `response_model` 序列化与过滤 |

这不是一一严格对应：Spring 的核心是长期存活的 IoC 容器和 Bean；FastAPI 的核心是请求到来时根据函数签名构建并执行依赖图。但用这张表建立直觉很有效。

## 1. 从启动开始：应用和路由如何被装配

项目入口在 [app/main.py](../app/main.py)：

```python
app = FastAPI(title=settings.app_name)
app.include_router(car_models_router)
```

这相当于创建 Web 应用并把一组 Controller 映射注册进去。`car_models_router` 定义在 [app/api/car_models.py](../app/api/car_models.py)：

```python
router = APIRouter(prefix="/car-models", tags=["car-models"])
```

因此该路由器中的路径都会以 `/car-models` 开头。它类似于：

```java
@RequestMapping("/car-models")
class CarModelController { ... }
```

但 FastAPI 不要求你创建 Controller 类。模块级的 `APIRouter` 加普通函数，就是它的常见组织方式。

## 2. 装饰器：不是执行接口，而是登记接口

车型列表接口：

```python
@router.get("", response_model=list[CarModelRead])
def list_car_models(...):
    ...
```

Python 装饰器语法可近似展开为：

```python
decorator = router.get("", response_model=list[CarModelRead])
list_car_models = decorator(list_car_models)
```

FastAPI 的 `APIRouter.get()` 本质上会调用通用的 `api_route()`，并固定传入 `methods=["GET"]`。后者返回的内部装饰器，会将函数和配置交给 `add_api_route()`：

```python
def decorator(func):
    self.add_api_route(
        path="",
        endpoint=func,
        response_model=list[CarModelRead],
        methods=["GET"],
    )
    return func
```

随后路由器保存一个近似如下的路由记录：

```text
path: /car-models       # router.prefix + ""
methods: [GET]
endpoint: list_car_models
response_model: list[CarModelRead]
```

所以模块导入、装饰器执行时，`list_car_models()` 不会查询数据库。框架只是在构建“请求到哪个函数”的映射表。这很像 Spring 在启动阶段扫描 `@RequestMapping` 并构建 `HandlerMapping`。

## 3. 一次创建车型请求的总流程

以 `POST /car-models` 为例：

```text
HTTP 请求进入 ASGI 服务器
    ↓
FastAPI / Starlette 根据 HTTP 方法和 URL 匹配 APIRoute
    ↓
读取函数签名，解析请求参数并计算依赖图
    ↓
执行 get_db()，创建数据库 Session，运行到 yield
    ↓
执行 OAuth2 token 提取 → get_current_user() → require_admin()
    ↓
解析 JSON 请求体，校验并构造 CarModelCreate
    ↓
调用 create_car_model(payload, database_session, current_user)
    ↓
按 response_model=CarModelRead 序列化和过滤返回值并发送 HTTP 响应
    ↓
请求处理栈退出，恢复 yield 依赖，执行 finally 关闭 Session
```

对应接口是：

```python
@router.post("", response_model=CarModelRead, status_code=status.HTTP_201_CREATED)
def create_car_model(
    payload: CarModelCreate,
    database_session: DatabaseSession,
    current_user: Annotated[object, Depends(require_admin)],
) -> CarModel:
    ...
```

Spring MVC 通常将这些能力分别表达在方法参数、参数注解、参数解析器、过滤器/拦截器和 Bean 注入中。FastAPI 则以“函数签名 + 类型标注”为主要声明位置。

## 4. 参数是从哪里来的

FastAPI 会根据参数的类型和注解推断数据来源。

### 4.1 请求体：Pydantic 模型

```python
payload: CarModelCreate
```

`CarModelCreate` 是 Pydantic 模型。FastAPI 看到它是复杂类型后，会从 JSON 请求体读取数据，验证字段并创建对象。这可近似理解为：

```java
public CarModel create(@Valid @RequestBody CarModelCreate payload)
```

字段缺失、类型不对或校验不通过时，业务函数不会运行，FastAPI 会返回 `422 Unprocessable Entity`。

### 4.2 查询参数和路径参数

```python
def list_car_models(
    brand_id: Annotated[int | None, Query(gt=0)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
```

这对应 `GET /car-models?brand_id=1&limit=20`。可类比：

```java
public List<CarModel> list(
    @RequestParam(required = false) @Positive Integer brandId,
    @RequestParam @Min(1) @Max(100) int limit
)
```

`@router.get("/{car_model_id}")` 中的 `car_model_id: int` 会被识别为路径参数，类似 `@PathVariable int carModelId`。

## 5. `Annotated`：类型和框架元数据放在一起

`Annotated` 来自 Python 标准库：

```python
from typing import Annotated
```

写法是：

```python
Annotated[真实类型, 元数据]
```

例如：

```python
Annotated[Session, Depends(get_db)]
```

这里 `Session` 表示最终传进来的对象类型，`Depends(get_db)` 则是 FastAPI 读取的元数据，表示“这个值由 `get_db` 提供”。

`Annotated` 本身不负责创建对象；它只是携带信息。真正读取 `Depends(...)`、调用依赖函数的是 FastAPI。

## 6. 依赖注入：`Depends` 如何工作

[app/core/dependencies.py](../app/core/dependencies.py) 定义了项目复用的数据库依赖类型：

```python
DatabaseSession = Annotated[Session, Depends(get_db)]
```

所以接口中的：

```python
database_session: DatabaseSession
```

等价于直接写：

```python
database_session: Annotated[Session, Depends(get_db)]
```

当 FastAPI 注册路由时，会分析处理函数及其依赖函数的参数，形成依赖图。请求到来后，再按图计算各个值。

```text
create_car_model
├─ payload: CarModelCreate             ← 请求体
├─ database_session: DatabaseSession   ← get_db()
└─ current_user                         ← require_admin()
   └─ current_user                       ← get_current_user()
      ├─ database_session               ← get_db()
      └─ token                          ← OAuth2PasswordBearer
```

同一次请求中，FastAPI 会缓存同一个依赖的结果。因此 `get_current_user()` 和路由函数需要的 `database_session` 会共享同一个 `Session`，而不是重复创建两个会话。

与 Spring 的关键差异是：

- Spring 常见写法是把 `DataSource`、Service、Repository 等对象作为 Bean 注入字段或构造器；
- FastAPI 常见写法是把“取得请求期数据或资源的方法”写进 `Depends(...)`；
- `get_db()` 每个请求创建一个 `Session`，但 `engine`、`SessionLocal` 是应用级共享对象。

## 7. `yield`：把依赖变成“前置 + 后置”的环绕逻辑

[app/core/database.py](../app/core/database.py) 中的数据库依赖：

```python
def get_db():
    database_session = SessionLocal()
    try:
        yield database_session
    finally:
        database_session.close()
```

含有 `yield` 的函数是生成器函数。调用 `get_db()` 时不会一口气执行到底；它先运行到 `yield`，把 `database_session` 交给 FastAPI，并暂停在这里。

请求处理结束时，FastAPI 恢复或关闭这个生成器，于是执行 `yield` 后面的退出逻辑。无论接口正常返回还是抛出异常，`finally` 都会执行。

可以把框架行为简化为：

```python
generator = get_db()
database_session = next(generator)  # 运行到 yield，取得 Session

try:
    result = create_car_model(database_session=database_session, ...)
finally:
    generator.close()                # 触发 finally，关闭 Session
```

从 Spring 的角度，它非常接近一个“只作用于声明该依赖的方法”的环绕通知：

```java
Session session = sessionFactory.openSession(); // 前置：创建资源
try {
    return controllerMethod(session);            // 执行业务
} finally {
    session.close();                             // 后置：保证清理
}
```

不过实现手段不同：这里不是 AOP 代理，而是 FastAPI 管理生成器依赖的生命周期。

## 8. 管理员权限：嵌套依赖链

创建车型接口声明：

```python
current_user: Annotated[object, Depends(require_admin)]
```

而 `require_admin` 又依赖 `get_current_user`：

```python
def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user
```

这条链的实际顺序是：

```text
OAuth2PasswordBearer：从 Authorization: Bearer <token> 取令牌
    ↓
get_current_user：解码令牌，用数据库查询用户；失败时抛出 401
    ↓
require_admin：检查 role；不是 admin 时抛出 403
    ↓
create_car_model：只有前面的依赖都成功才会执行
```

这在职责上接近 Spring Security 的认证与授权过滤链，但声明位置更靠近端点方法。`_ = current_user` 不参与业务逻辑；它只是显式表明该参数的目的在于触发管理员校验。

## 9. 业务执行、事务与响应模型

权限和请求体校验通过后，才会执行接口函数中的业务逻辑：

```python
require_brand(payload.brand_id, database_session)
car_model = CarModel(**payload.model_dump())
database_session.add(car_model)
database_session.commit()
database_session.refresh(car_model)
return car_model
```

这里的 `Session` 类似 JPA 的持久化上下文，但使用方式更显式：

- `add()`：把 ORM 实体纳入当前会话；
- `commit()`：提交当前事务；
- `refresh()`：从数据库重新读取实体，取得数据库生成的字段，如主键；
- `close()`：请求结束后，由 `get_db()` 的 `finally` 执行。

注意：`close()` 是关闭会话/归还连接资源，不等于自动 `commit()`。当前项目是在每个写操作中显式调用 `commit()`。这与 Spring 的 `@Transactional` 自动提交或回滚有所不同；若要实现类似统一事务边界，需要额外设计事务依赖或服务层事务策略。

函数返回的是 SQLAlchemy 的 `CarModel` 实体，但路由声明了：

```python
response_model=CarModelRead
```

FastAPI 会使用 Pydantic 将返回值转换为响应 JSON，并只保留 `CarModelRead` 中声明的字段。这个角色类似 Spring Boot 使用 Jackson 按 DTO 进行响应序列化：避免把 ORM 对象的内部字段、敏感字段或未约定字段直接暴露给客户端。

## 10. 正常与异常路径

### 正常创建

```text
POST /car-models
  → 路由匹配
  → 创建 Session
  → 验证 token 和 admin 角色
  → 校验 JSON 为 CarModelCreate
  → 校验品牌存在
  → 保存并提交车型
  → 按 CarModelRead 序列化并发送 201 响应
  → 请求处理栈退出后关闭 Session
```

### 请求体不合法

```text
POST /car-models
  → 路由匹配
  → 参数校验失败
  → 返回 422
  → 已启动的 yield 依赖执行退出清理
```

### 不是管理员

```text
POST /car-models
  → 创建 Session
  → 身份认证成功
  → require_admin 抛出 HTTPException(403)
  → 业务函数不执行
  → Session 在 finally 中关闭
  → 返回 403
```

### 品牌不存在

```text
POST /car-models
  → 所有前置校验通过
  → require_brand 抛出 HTTPException(404)
  → 不提交车型
  → Session 在 finally 中关闭
  → 返回 404
```

`HTTPException` 相当于在业务代码中抛出一个框架能识别的 HTTP 异常；FastAPI 会将其转换为对应状态码和 JSON 响应，而不是把它当成未处理的 500 异常。

## 11. 用一句话串起核心机制

FastAPI 在启动时通过装饰器把函数登记成路由；在每次请求到来时，根据函数签名解析请求数据和依赖图，先执行依赖、再执行业务函数，之后按响应模型生成 JSON，并保证 `yield` 依赖在结束时清理资源。

当你阅读一个 FastAPI 接口时，可以按下面顺序看：

1. 看 `@router.get/post`：URL、HTTP 方法、响应模型；
2. 看函数参数：哪些来自请求，哪些来自 `Depends`；
3. 展开 `Depends`：认证、权限、数据库等前置条件；
4. 看函数体：真正的业务逻辑和事务提交点；
5. 看 `response_model`：客户端最终能看到什么字段；
6. 看 `yield` 依赖：资源何时创建、何时必定释放。

掌握这条阅读路径后，FastAPI 的函数式写法就可以对应回你熟悉的 Spring Boot 请求处理模型：路由映射、参数绑定、依赖准备、权限校验、业务处理、序列化响应、资源清理。
