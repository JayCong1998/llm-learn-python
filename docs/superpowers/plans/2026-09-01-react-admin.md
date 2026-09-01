# React 车辆后台管理实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个可登录并管理 FastAPI 品牌、车型数据的 React 后台。

**架构：** Vite 开发服务器将 `/api` 代理到 FastAPI；`api/client.ts` 统一发请求和处理鉴权错误。页面仅编排状态与组件，品牌、车型表单通过受控组件完成数据写入并重新加载列表。

**技术栈：** React、TypeScript、Vite、Vitest、React Testing Library。

---

## 文件结构

- `react-admin/package.json`：前端命令与依赖。
- `react-admin/vite.config.ts`：开发代理和测试环境。
- `react-admin/src/api/client.ts`：认证头、错误转换和 HTTP 请求。
- `react-admin/src/api/resources.ts`：登录、品牌、车型接口函数。
- `react-admin/src/auth/session.ts`：JWT 持久化。
- `react-admin/src/types.ts`：与 FastAPI schema 对齐的类型。
- `react-admin/src/App.tsx`：登录保护、导航和页面编排。
- `react-admin/src/pages/*.tsx`：登录、品牌、车型页面。
- `react-admin/src/components/*.tsx`：通用弹窗、品牌表单、车型表单。
- `react-admin/src/**/*.test.tsx`：接口、会话、登录和表单测试。

### 任务 1：搭建项目与测试基线

**文件：**
- 创建：`react-admin/package.json`、`react-admin/vite.config.ts`、`react-admin/src/main.tsx`、`react-admin/src/index.css`

- [ ] 编写基础渲染测试，导入尚不存在的 `App` 并断言页面包含「管理员后台」。
- [ ] 运行 `npm test -- --run`，预期因 `App` 不存在而失败。
- [ ] 创建 Vite、TypeScript、Vitest 与 Testing Library 配置，以及最小 `App` 实现。
- [ ] 运行 `npm test -- --run`，预期通过。
- [ ] 提交 `feat: scaffold React admin`。

### 任务 2：实现会话与 HTTP 客户端

**文件：**
- 创建：`react-admin/src/auth/session.ts`、`react-admin/src/api/client.ts`
- 测试：`react-admin/src/auth/session.test.ts`、`react-admin/src/api/client.test.ts`

- [ ] 编写会话测试：保存 Token 后可读取，清除后为空；编写客户端测试：受保护请求带 Bearer Token，401 清除会话并抛出可展示错误。
- [ ] 运行 `npm test -- --run src/auth/session.test.ts src/api/client.test.ts`，预期因模块缺失失败。
- [ ] 实现 `getToken`、`setToken`、`clearToken` 与 `request<T>`，将非成功响应的 `detail` 转为 `ApiError`。
- [ ] 重跑同一测试命令，预期全部通过。
- [ ] 提交 `feat: add authenticated API client`。

### 任务 3：封装后端资源接口与类型

**文件：**
- 创建：`react-admin/src/types.ts`、`react-admin/src/api/resources.ts`
- 测试：`react-admin/src/api/resources.test.ts`

- [ ] 编写失败测试，断言 `login` 向 `/api/auth/login` 发送用户名密码，`listCarModels(2)` 请求 `/api/car-models?brand_id=2`。
- [ ] 运行 `npm test -- --run src/api/resources.test.ts`，预期因函数缺失失败。
- [ ] 定义 `Brand`、`BrandPayload`、`CarModel`、`CarModelPayload` 与 `TokenResponse`，并实现所有品牌、车型 CRUD 与登录函数。
- [ ] 重跑资源接口测试，预期通过。
- [ ] 提交 `feat: add FastAPI resource clients`。

### 任务 4：实现登录与管理框架

**文件：**
- 创建：`react-admin/src/pages/LoginPage.tsx`、`react-admin/src/components/Layout.tsx`
- 修改：`react-admin/src/App.tsx`
- 测试：`react-admin/src/pages/LoginPage.test.tsx`

- [ ] 编写失败测试，填写用户名密码并提交后调用 `login`、保存 Token、显示品牌管理；登录失败显示「用户名或密码错误」。
- [ ] 运行 `npm test -- --run src/pages/LoginPage.test.tsx`，预期失败。
- [ ] 实现登录表单、加载状态、错误展示、Token 保存、登录守卫、左侧导航和退出行为。
- [ ] 重跑登录页测试，预期通过。
- [ ] 提交 `feat: add authenticated admin layout`。

### 任务 5：实现品牌 CRUD 页面

**文件：**
- 创建：`react-admin/src/pages/BrandsPage.tsx`、`react-admin/src/components/BrandForm.tsx`
- 修改：`react-admin/src/App.tsx`
- 测试：`react-admin/src/pages/BrandsPage.test.tsx`

- [ ] 编写失败测试：页面加载品牌列表；提交新增表单后调用创建接口并刷新；删除需确认且调用删除接口。
- [ ] 运行 `npm test -- --run src/pages/BrandsPage.test.tsx`，预期失败。
- [ ] 实现品牌表格、新增/编辑弹窗、确认删除、请求错误和写入后的重新加载。
- [ ] 重跑品牌测试，预期通过。
- [ ] 提交 `feat: add brand management`。

### 任务 6：实现车型 CRUD 与筛选页面

**文件：**
- 创建：`react-admin/src/pages/CarModelsPage.tsx`、`react-admin/src/components/CarModelForm.tsx`
- 修改：`react-admin/src/App.tsx`
- 测试：`react-admin/src/pages/CarModelsPage.test.tsx`

- [ ] 编写失败测试：加载品牌选项与车型；选择品牌时带 `brand_id` 查询；提交车型表单时传递 `name`、`year`、`price`、`brand_id`。
- [ ] 运行 `npm test -- --run src/pages/CarModelsPage.test.tsx`，预期失败。
- [ ] 实现筛选器、车型表格、品牌名称映射、新增/编辑弹窗、确认删除与错误展示。
- [ ] 重跑车型测试，预期通过。
- [ ] 提交 `feat: add car model management`。

### 任务 7：完整验证与使用说明

**文件：**
- 创建：`react-admin/README.md`

- [ ] 记录 `npm install`、`npm run dev`、后端启动顺序和 `VITE_API_BASE_URL` 配置。
- [ ] 运行 `npm test -- --run`，预期全部测试通过。
- [ ] 运行 `npm run build`，预期 Vite 生产构建成功。
- [ ] 在已启动的 FastAPI 服务上执行一次登录与品牌、车型 CRUD 人工联调，记录阻塞项或结果。
- [ ] 提交 `docs: add React admin usage`。
