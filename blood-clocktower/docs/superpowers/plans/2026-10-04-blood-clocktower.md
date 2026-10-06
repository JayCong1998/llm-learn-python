# 血染钟楼多智能体游戏实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在本地提供一名人类与多名独立 AI 玩家共同完成一局 Trouble Brewing 的游戏，支持 5–15 个座位和全部 22 个角色。

**Architecture:** FastAPI 暴露经过隐私投影的游戏视图与动作接口；领域规则独立裁定角色能力；LangChain `PlayerAgent` 按座位使用私有上下文生成对话和行动；LangGraph 使用可恢复状态图编排昼夜阶段并在等待人类时中断；Vue 3 前端通过 HTTP 与 SSE 连接游戏。

**Tech Stack:** Python 3.14.3、FastAPI、Pydantic、LangChain `ChatOpenAI`、LangGraph `StateGraph`、`langgraph-checkpoint-sqlite`、pytest、Vue 3、TypeScript、Vite、Vue Router、Pinia、Vitest、pnpm。

**Spec:** `docs/superpowers/specs/2026-10-04-blood-clocktower-design.md`

## Global Constraints

- 对局人数为 5–15，含 1 名人类玩家；默认 8 人，角色从 Trouble Brewing 全部 22 个角色中按人数配置抽取。
- 使用 Python、LangChain `ChatOpenAI` 和 LangGraph；checkpointer 依赖最低版本为 `langgraph>=1.0.10`、`langgraph-checkpoint>=4.1.1`、`langgraph-checkpoint-sqlite>=3.0.1`。
- 在导入 LangGraph 前设置 `LANGGRAPH_STRICT_MSGPACK=true`；SQLite checkpoint 仅用于单进程本地游戏，严禁返回完整内部状态给客户端。
- 前端必须使用 Vue 3、TypeScript、Vite、Vue Router 和 Pinia；用 pnpm 锁定 JavaScript 依赖，Python 依赖也须提交锁文件。
- 模型离线、未配置密钥或输出错误时，必须走显式可见的本地策略，且同一动作 schema 和规则校验仍适用。
- 规则层决定合法动作、信息、死亡、投票、设置变更和胜负；Agent 只提议话语/行动，不能改写游戏状态。
- 每个 AI 座位有独立记忆和规则授权的视图；Drunk 不得获知真实身份，Spy 只在能力允许时得到 Grimoire；SSE 只发公开事件或当前人类依法可见的私密事件。
- 所有新增或修改的有效 Python 代码行前一行必须有准确简短的中文独立注释；密钥不得进入源代码、注释、测试输出或 Git。
- 所有产品文件与提交都限制在 `blood-clocktower/`；提交使用任务文件路径，不能带入父仓库或 `agent-langchain/` 的既有改动。

## Review Focus

- 玩家数边界 5/15、角色类别人数以及 Baron 改变人数的结果符合配置表；由 Task 2 的 `test_player_counts_cover_five_through_fifteen` 和 `test_baron_replaces_two_townsfolk` 覆盖。
- Drunk 只认知为一名不在场的镇民且没有真实能力；Recluse/Spy 的注册、Spy 的 Grimoire、恶魔 bluff 和邪恶队伍初始信息不会在 Agent/API/SSE 视图间串漏；由 Task 2、Task 3、Task 6 和 Task 8 的私有视图测试覆盖。
- 夜晚行动顺序、一次性能力、角色死亡触发和胜利优先级在交互时仍正确；由 Task 4、Task 5 的角色交互测试覆盖。
- LangGraph 在 interrupt、重启恢复和重复 action ID 下不重复执行副作用；由 Task 7、Task 8 的恢复与幂等测试覆盖。
- 未配置模型、超时和无效结构化输出不阻塞对局也不产生越权动作；由 Task 6、Task 10 的本地策略和端到端测试覆盖。

---

## File Structure

- `backend/requirements.in`：运行依赖输入清单。
- `backend/requirements-dev.in`：包含运行依赖与开发/测试工具的输入清单。
- `backend/requirements.lock`、`backend/requirements-dev.lock`：Python 锁定依赖。
- `backend/pytest.ini`：固定 pytest 根目录和后端导入路径。
- `backend/app/main.py`：FastAPI 应用创建、生命周期和路由挂载。
- `backend/app/api/`：HTTP 请求/响应 schema、health、game 与 SSE 路由。
- `backend/app/application/`：游戏用例、动作编排、事件读取和视图投影。
- `backend/app/domain/`：可序列化领域实体、阶段与阵营类型、22 角色目录及规则服务。
- `backend/app/domain/services/storyteller.py`：集中处理规则允许的注册、虚假信息与 Storyteller 选择。
- `backend/app/agents/`：玩家上下文过滤、输出 schema、模型工厂、本地策略和 `PlayerAgent`。
- `backend/app/gameflow/`：LangGraph 状态、节点、条件路由、构图与 SQLite checkpointer 工厂。
- `backend/tests/domain/`：setup、角色信息、夜晚、白天和胜负的规则单测。
- `backend/tests/agents/`：Agent 输入隔离、schema、模型失败和本地策略测试。
- `backend/tests/gameflow/`：LangGraph 阶段、interrupt/resume、重启和 action 幂等测试。
- `backend/tests/api/`：FastAPI 视图隐私、命令、SSE 和 health 测试。
- `backend/tests/e2e/`：本地策略下的完整游戏路径与胜负场景。
- `backend/tests/conftest.py`：在 pytest 导入测试模块和 LangGraph 前开启严格 checkpoint 序列化模式。
- `frontend/src/router/`、`frontend/src/stores/`、`frontend/src/services/`：页面路由、Pinia 状态与 API/SSE 客户端。
- `frontend/src/views/`、`frontend/src/components/`：开始页、对局页、座位、讨论、私密信息、行动和结局组件。
- `frontend/src/types/`：后端视图与命令的 TypeScript 契约。
- `frontend/src/**/*.spec.ts`：Vitest 前端状态/组件测试。
- `scripts/run_backend.ps1`：先设 checkpoint 安全环境，再启动本地后端。
- `.env.example`、`.gitignore`、`README.md`：本地配置、忽略数据和完整学习/启动文档。

## Task 1: 项目骨架与开发环境

**Files:**
- Create: `backend/requirements.in`
- Create: `backend/requirements-dev.in`
- Create: `backend/requirements.lock`
- Create: `backend/requirements-dev.lock`
- Create: `backend/pytest.ini`
- Create: `backend/tests/conftest.py`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/health.py`
- Create: `backend/tests/api/test_health.py`
- Create: `frontend/` Vue 3 + TypeScript + Vite scaffold and `frontend/pnpm-lock.yaml`
- Create: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/index.html`, `frontend/tsconfig.json`
- Create: `frontend/src/__tests__/home.spec.ts`
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/views/HomeView.vue`
- Create: `frontend/src/App.vue`
- Create: `scripts/run_backend.ps1`
- Create: `.env.example`
- Create: `.gitignore`

**Interfaces:**
- Produces: `GET /api/health` returns HTTP 200 with `{"status":"ok"}`; Vite serves the Vue router home page.
- Runtime requirements include FastAPI, Uvicorn, Pydantic settings, LangChain, LangChain OpenAI, LangGraph, SQLite checkpointer, aiosqlite and dotenv; dev requirements include pytest, HTTPX and pip-tools.
- Test bootstrap sets `LANGGRAPH_STRICT_MSGPACK=true` before test collection imports application modules; frontend dev dependencies include Vitest, Vue Test Utils and jsdom.
- `scripts/run_backend.ps1` sets `LANGGRAPH_STRICT_MSGPACK=true` before importing the application.

- [ ] **Step 1: Write failing backend and frontend smoke tests**

Create `test_health.py::test_health_endpoint_returns_ok`. Add a minimal frontend package manifest with the test script and test tooling, plus a Vitest home-route smoke test asserting the root route renders the game title; leave the app component and route implementation absent so the test fails for the intended reason.

- [ ] **Step 2: Run the smoke tests and confirm they fail**

Run: `python -m pytest backend/tests/api/test_health.py -q`  
Expected: FAIL because the API module and health route do not exist.

Run: `pnpm --dir frontend test -- --run`  
Expected: FAIL because the home view and router implementation do not exist.

- [ ] **Step 3: Scaffold backend and frontend**

Create FastAPI health routing and the Vue 3 TypeScript Vite app with Vue Router and Vitest. Configure pytest's backend import path and strict LangGraph serializer environment in `backend/pytest.ini` and `backend/tests/conftest.py` before collection. Generate Python locks with pip-tools and the frontend lock with pnpm. Add the local launcher and ignore `.env`, SQLite files, virtual environments, `node_modules` and build output.

- [ ] **Step 4: Run smoke tests and production build**

Run: `python -m pytest backend/tests/api/test_health.py -q`  
Expected: PASS with one health test.

Run: `pnpm --dir frontend test -- --run` and `pnpm --dir frontend build`  
Expected: PASS and a production bundle is emitted.

- [ ] **Step 5: Commit only Task 1 files**

Commit message: `chore: scaffold blood clocktower app`.

## Task 2: Domain types, all-role catalogue and setup

**Files:**
- Create: `backend/app/domain/__init__.py`
- Create: `backend/app/domain/enums.py`
- Create: `backend/app/domain/entities.py`
- Create: `backend/app/domain/characters/__init__.py`
- Create: `backend/app/domain/characters/catalog.py`
- Create: `backend/app/domain/rules/__init__.py`
- Create: `backend/app/domain/rules/setup.py`
- Create: `backend/tests/domain/test_character_catalog.py`
- Create: `backend/tests/domain/test_setup.py`

**Interfaces:**
- `get_player_counts(player_count: int) -> PlayerCounts` returns the exact 5–15 roster table.
- `build_game_setup(settings: GameSettings, rng: RandomSource) -> GameState` creates the secret assignment for one human and the remaining AI seats.
- `apply_setup_modifiers(roster: list[CharacterId]) -> list[CharacterId]` applies the in-play Baron effect without changing player count.
- `PlayerState` separately stores true character, perceived character, known alignment, living/dead state, drunk/poisoned state, vote token, one-use flags and seat-local memory.
- `CharacterDefinition` provides stable ID, Chinese/English names, category, paraphrased ability, timing and action schema for all 22 roles.

- [ ] **Step 1: Write failing roster and catalogue tests**

Add `test_player_counts_cover_five_through_fifteen`, `test_player_counts_reject_unsupported_sizes`, `test_baron_replaces_two_townsfolk`, `test_setup_assigns_one_human_and_valid_categories`, `test_setup_is_reproducible_for_same_seed_and_varies_across_seed_set`, `test_drunk_gets_out_of_play_townsfolk_perception_without_ability`, and `test_catalogue_contains_all_twenty_two_trouble_brewing_roles`.

- [ ] **Step 2: Run the domain tests and confirm they fail**

Run: `python -m pytest backend/tests/domain/test_character_catalog.py backend/tests/domain/test_setup.py -q`  
Expected: FAIL because domain entities, role definitions and setup rules do not exist.

- [ ] **Step 3: Implement domain entities, catalogue and setup rules**

Create serializable game/seat/action types, bilingual role metadata, the 5–15 counts table, seeded test randomness, secret production assignment, Baron count replacement and Drunk's apparent out-of-play Townsfolk identity, without granting the apparent ability.

- [ ] **Step 4: Run the domain tests**

Run: `python -m pytest backend/tests/domain/test_character_catalog.py backend/tests/domain/test_setup.py -q`  
Expected: PASS; every role is represented and all roster compositions match the table.

- [ ] **Step 5: Commit only Task 2 files**

Commit message: `feat: model trouble brewing roles and setup`.

## Task 3: Starting information, nightly information and registration

**Files:**
- Create: `backend/app/domain/rules/information.py`
- Create: `backend/app/domain/rules/registration.py`
- Create: `backend/app/domain/services/__init__.py`
- Create: `backend/app/domain/services/storyteller.py`
- Create: `backend/tests/domain/test_information.py`
- Create: `backend/tests/domain/test_registration.py`

**Interfaces:**
- `deliver_starting_information(state: GameState) -> list[PrivateEvent]` emits each seat only the opening information it is entitled to receive.
- `deliver_night_information(state: GameState, night: int) -> list[PrivateEvent]` resolves recurring information abilities and their timing.
- `StorytellerPolicy.choose_registration(state: GameState, actor_id: str, target_id: str, ability: AbilityId) -> Registration` deterministically records permitted Spy/Recluse registration for an information ability.
- `StorytellerPolicy.make_information(state: GameState, recipient_id: str, true_result: InformationResult) -> InformationResult` returns truthful or rules-permitted false information and records why.
- `StorytellerPolicy.choose_red_herring(state: GameState, fortune_teller_id: str) -> str` selects and persists one eligible red herring for that Fortune Teller.

- [ ] **Step 1: Write failing information and registration tests**

Add tests for Washerwoman, Librarian (including zero Outsiders), Investigator, Chef circular adjacency, Empath living neighbors, Fortune Teller red herring, Undertaker after execution, initial evil-team/bluff knowledge, Drunk false information consistent with its perceived Townsfolk role, Spy Grimoire access, and Spy/Recluse registration that remains possible after death.

- [ ] **Step 2: Run tests and confirm they fail**

Run: `python -m pytest backend/tests/domain/test_information.py backend/tests/domain/test_registration.py -q`  
Expected: FAIL because information delivery and registration policy do not exist.

- [ ] **Step 3: Implement information delivery and Storyteller policy**

Use only canonical game state to calculate true information; apply Drunk/Poisoner misinformation and character registration in a separate policy; allow the Drunk's apparent role to produce unreliable information without activating its ability; store private results as seat-scoped events.

- [ ] **Step 4: Run all information tests**

Run: `python -m pytest backend/tests/domain/test_information.py backend/tests/domain/test_registration.py -q`  
Expected: PASS with every listed information role isolated to valid recipients.

- [ ] **Step 5: Commit only Task 3 files**

Commit message: `feat: resolve trouble brewing information abilities`.

## Task 4: Night action collection and resolution

**Files:**
- Create: `backend/app/domain/rules/night.py`
- Create: `backend/app/domain/rules/abilities/night.py`
- Modify: `backend/app/domain/services/storyteller.py`
- Create: `backend/tests/domain/test_night_resolution.py`

**Interfaces:**
- `get_night_actions(state: GameState, seat_id: str) -> list[AvailableAction]` returns only actions valid for that seat and night.
- `resolve_night(state: GameState, actions: list[AcceptedAction]) -> RuleResult` resolves actions in Trouble Brewing timing order and returns updated state plus ordered events.
- `RuleResult` carries immutable state updates and events; no handler mutates a shared game object in place.

- [ ] **Step 1: Write failing night-action tests**

Add tests for Poisoner timing, Monk protection, Imp attack and self-kill transfer, Soldier immunity, Ravenkeeper death-triggered information, Scarlet Woman succession only at the correct living-player threshold, Mayor redirection, living Spy Grimoire visibility, dead Spy/Recluse registration, Drunk apparent-ability no-op, and dead-player ability loss.

- [ ] **Step 2: Run tests and confirm they fail**

Run: `python -m pytest backend/tests/domain/test_night_resolution.py -q`  
Expected: FAIL because night actions and role handlers do not exist.

- [ ] **Step 3: Implement ordered night resolution**

Separate action validation, poisoning/protection effects, attack/death resolution, death-triggered abilities, role succession and emitted events. Derive each player's available action from role state, not from LLM output; an apparent Drunk ability may be presented as learned but its action cannot alter game state.

- [ ] **Step 4: Run night-resolution tests**

Run: `python -m pytest backend/tests/domain/test_night_resolution.py -q`  
Expected: PASS for each role and interaction in the test list.

- [ ] **Step 5: Commit only Task 4 files**

Commit message: `feat: resolve trouble brewing night actions`.

## Task 5: Day actions, executions and victory rules

**Files:**
- Create: `backend/app/domain/rules/day.py`
- Create: `backend/app/domain/rules/victory.py`
- Create: `backend/app/domain/rules/abilities/day.py`
- Create: `backend/tests/domain/test_day_resolution.py`
- Create: `backend/tests/domain/test_victory.py`

**Interfaces:**
- `get_day_actions(state: GameState, seat_id: str) -> list[AvailableAction]` returns legal discussion, nomination, vote and once-per-game actions.
- `resolve_day_action(state: GameState, action: AcceptedAction) -> RuleResult` validates and applies one action without advancing unauthorized phases.
- `determine_winner(state: GameState) -> Team | None` applies all immediate and threshold win conditions.
- `execution_threshold(alive_count: int) -> int` returns the minimum votes required by the rules.
- `StorytellerPolicy.choose_mayor_redirect(state: GameState, attacked_id: str) -> str | None` returns the selected alternate target or no redirect when Mayor's night ability permits it.

- [ ] **Step 1: Write failing day and victory tests**

Add tests for one nomination per player, dead-player speech and one remaining vote, Butler master-vote restriction, majority threshold, tied/under-threshold votes, maximum one execution, Virgin's first qualifying Townsfolk nomination (and no trigger from a Drunk with an apparent Townsfolk role), Slayer's once-per-game Demon hit, Saint execution, Mayor three-player no-execution victory, Demon death, Scarlet Woman replacement and evil victory at two alive.

- [ ] **Step 2: Run tests and confirm they fail**

Run: `python -m pytest backend/tests/domain/test_day_resolution.py backend/tests/domain/test_victory.py -q`  
Expected: FAIL because day actions and victory calculation do not exist.

- [ ] **Step 3: Implement day resolution and terminal checks**

Keep nominations, votes, execution effects and victory checks as explicit domain transitions. Ensure Virgin's immediate execution consumes that day's execution and all death effects are applied before selecting a winner.

- [ ] **Step 4: Run day and victory tests**

Run: `python -m pytest backend/tests/domain/test_day_resolution.py backend/tests/domain/test_victory.py -q`  
Expected: PASS for all voting, role triggers and both team outcomes.

- [ ] **Step 5: Commit only Task 5 files**

Commit message: `feat: resolve town voting and victory conditions`.

## Task 6: LangChain player agents and deterministic local strategy

**Files:**
- Create: `backend/app/agents/__init__.py`
- Create: `backend/app/agents/contracts.py`
- Create: `backend/app/agents/context.py`
- Create: `backend/app/agents/factory.py`
- Create: `backend/app/agents/player.py`
- Create: `backend/app/agents/local_policy.py`
- Create: `backend/app/agents/prompts.py`
- Create: `backend/tests/agents/test_agent_context.py`
- Create: `backend/tests/agents/test_player_agent.py`
- Create: `backend/tests/agents/test_local_policy.py`

**Interfaces:**
- `build_player_context(state: GameState, seat_id: str, task: AgentTask) -> PlayerContext` projects only that seat's public and private knowledge.
- `AgentDecision` is a Pydantic schema with `speech`, optional `action_type`, optional `target_id` and a constrained rationale code; no free-form hidden reasoning is stored or exposed.
- `PlayerAgent.decide(context: PlayerContext) -> AgentDecision` uses a LangChain prompt/model structured-output chain or the local policy behind one interface.
- `create_player_agent(settings: ModelSettings, seat_id: str) -> PlayerAgent` creates independent seat memory while sharing only the stateless model client.

- [ ] **Step 1: Write failing Agent contract and privacy tests**

Add tests proving Drunk receives only its perceived out-of-play Townsfolk role and normal role description without the server-side Drunk identity, Spy receives Grimoire data only through its ability-gated context while alive, good players never see evil-team private data, seat memories do not mix, and returned actions conform to Pydantic constraints.

- [ ] **Step 2: Run Agent tests and confirm they fail**

Run: `python -m pytest backend/tests/agents -q`  
Expected: FAIL because the Agent contracts and context projection do not exist.

- [ ] **Step 3: Implement LangChain and local PlayerAgent providers**

Build one structured-output chain per seat context using configured model/base URL; implement stable Chinese role voices and a deterministic legal-action policy. Retry one invalid model output, then use the local strategy and produce a visible fallback event.

- [ ] **Step 4: Run Agent tests with fake models and no API key**

Run: `python -m pytest backend/tests/agents -q`  
Expected: PASS without external requests; bad model responses fall back to valid legal decisions.

- [ ] **Step 5: Commit only Task 6 files**

Commit message: `feat: add isolated langchain player agents`.

## Task 7: LangGraph phases, interrupts and SQLite recovery

**Files:**
- Create: `backend/app/gameflow/__init__.py`
- Create: `backend/app/gameflow/state.py`
- Create: `backend/app/gameflow/checkpoint.py`
- Create: `backend/app/gameflow/nodes/setup.py`
- Create: `backend/app/gameflow/nodes/night.py`
- Create: `backend/app/gameflow/nodes/day.py`
- Create: `backend/app/gameflow/builder.py`
- Create: `backend/tests/gameflow/test_graph_phases.py`
- Create: `backend/tests/gameflow/test_graph_recovery.py`

**Interfaces:**
- `GameGraphState` is a typed serializable LangGraph state containing domain state, pending human prompt, processed action IDs, public/private event log and phase cursor.
- `create_checkpointer(database_path: Path) -> AsyncSqliteSaver` creates the strict-mode saver using a supported serializer configuration.
- `build_game_graph(checkpointer: BaseCheckpointSaver) -> CompiledStateGraph` compiles setup, night, discussion, nomination/voting, resolution and victory nodes with explicit conditional edges.
- Every human pause uses `interrupt`; resumption uses `Command(resume=...)` with the same game ID as LangGraph `thread_id`.

- [ ] **Step 1: Write failing graph progression and recovery tests**

Add tests for setup-to-first-night progress, first-night human pause, resume into AI night actions, a day/night loop, SQLite close/reopen recovery, repeated action ID rejection and exactly-once event emission.

- [ ] **Step 2: Run graph tests and confirm they fail**

Run: `python -m pytest backend/tests/gameflow -q`  
Expected: FAIL because graph state, nodes and checkpointer do not exist.

- [ ] **Step 3: Implement compiled graph and persistent checkpoints**

Create phase nodes that call Domain and PlayerAgent interfaces; advance AI actions until the next human decision; persist after each transition; enforce action ID before side effects. Initialize strict checkpoint mode before LangGraph imports.

- [ ] **Step 4: Run graph tests against a temporary SQLite database**

Run: `python -m pytest backend/tests/gameflow -q`  
Expected: PASS, including restoration from a newly opened saver after simulated process shutdown.

- [ ] **Step 5: Commit only Task 7 files**

Commit message: `feat: orchestrate games with resumable langgraph`.

## Task 8: Application service, private views, HTTP and SSE

**Files:**
- Create: `backend/app/application/__init__.py`
- Create: `backend/app/application/game_service.py`
- Create: `backend/app/application/projections.py`
- Create: `backend/app/application/event_stream.py`
- Create: `backend/app/api/schemas.py`
- Create: `backend/app/api/games.py`
- Create: `backend/app/api/events.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/api/test_games.py`
- Create: `backend/tests/api/test_game_privacy.py`
- Create: `backend/tests/api/test_sse.py`

**Interfaces:**
- `GameService.create_game(request: CreateGameRequest) -> GameView` starts a game and returns the human seat's permitted opening view.
- `GameService.submit_action(game_id: str, seat_token: str, command: PlayerCommand) -> GameView` validates human ownership, action ID and phase before resuming the graph.
- `GameService.get_view(game_id: str, seat_token: str) -> GameView` returns public state plus only the human's authorized private information.
- `GameService.stream_events(game_id: str, seat_token: str, last_event_id: str | None) -> AsyncIterator[GameEvent]` resumes after an event ID and filters by visibility.
- HTTP routes implement `POST /api/games`, `GET /api/games/{game_id}`, `POST /api/games/{game_id}/actions`, and `GET /api/games/{game_id}/events`.

- [ ] **Step 1: Write failing API, privacy and reconnect tests**

Add tests for create/read/action, invalid-phase action with unchanged checkpoint, repeated action ID, Drunk private view, Spy ability-gated view, no public alignment/role leak, evil-team event filtering and SSE replay after a last-event ID.

- [ ] **Step 2: Run API tests and confirm they fail**

Run: `python -m pytest backend/tests/api -q`  
Expected: FAIL because game routes and projection services do not exist.

- [ ] **Step 3: Implement application service and routes**

Make service layer the sole path between API and graph; validate seat token and command schema; return typed errors; stream only filtered events with stable IDs; never expose raw LangGraph checkpoints.

- [ ] **Step 4: Run API tests**

Run: `python -m pytest backend/tests/api -q`  
Expected: PASS; invalid commands do not mutate state and private events reach only their authorized seat.

- [ ] **Step 5: Commit only Task 8 files**

Commit message: `feat: expose filtered game api and event stream`.

## Task 9: Vue game setup and playable table

**Files:**
- Create: `frontend/src/types/game.ts`
- Create: `frontend/src/services/gameApi.ts`
- Create: `frontend/src/stores/game.ts`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/views/HomeView.vue`
- Create: `frontend/src/views/GameView.vue`
- Create: `frontend/src/components/GameTable.vue`
- Create: `frontend/src/components/PlayerSeat.vue`
- Create: `frontend/src/components/PublicDiscussion.vue`
- Create: `frontend/src/components/PrivateInfoPanel.vue`
- Create: `frontend/src/components/ActionPanel.vue`
- Create: `frontend/src/components/GameEndSummary.vue`
- Create: `frontend/src/components/ActionPanel.spec.ts`
- Create: `frontend/src/stores/game.spec.ts`

**Interfaces:**
- `gameApi.createGame`, `getGame`, `submitAction` and `subscribeEvents` implement the API contracts from Task 8.
- Pinia `useGameStore` exposes `gameView`, `availableActions`, `connectionState`, `pendingAction` and `lastEventId`; it stores only filtered server views.
- `GameView.vue` subscribes to SSE, reloads the HTTP view on reconnect and uses `available_actions` to render legal controls.

- [ ] **Step 1: Write failing store and action-panel tests**

Add tests for displaying only server-authorized controls, preventing double submission while an action is pending, separating private information from public chat, and applying/replaying an SSE event once. Add or update Vue Test Utils/jsdom dependencies and refresh `frontend/pnpm-lock.yaml` if Task 1 did not include them.

- [ ] **Step 2: Run frontend tests and confirm they fail**

Run: `pnpm --dir frontend test -- --run`  
Expected: FAIL because the game store and components do not exist.

- [ ] **Step 3: Implement game setup and table UI**

Build a responsive Chinese-first game table with bilingual role names, alive/dead seats, public discussion, private panel, phase-specific action controls and end-of-game reveal. Connect REST commands and SSE events to Pinia.

- [ ] **Step 4: Run frontend tests and production build**

Run: `pnpm --dir frontend test -- --run` and `pnpm --dir frontend build`  
Expected: PASS; controls and private panels follow server projections.

- [ ] **Step 5: Commit only Task 9 files**

Commit message: `feat: build vue clocktower game table`.

## Task 10: Complete-game verification and learning docs

**Files:**
- Create: `backend/tests/e2e/test_complete_game.py`
- Create: `backend/tests/e2e/test_restart_midgame.py`
- Create: `README.md`
- Modify: `.env.example`
- Modify: `scripts/run_backend.ps1`
- Modify: `.gitignore`

**Interfaces:**
- E2E harness starts an 8-seat game in deterministic local mode, supplies the human commands through the same `GameService` interface as the UI, and returns the public event log plus terminal winner.
- README documents Windows PowerShell startup, model settings, local mode, ports, dependency locks, route map, game phases and LangChain/LangGraph/Domain/Vue data flow.

- [ ] **Step 1: Write failing full-game tests**

Add `test_complete_game_reaches_good_victory`, `test_complete_game_reaches_evil_victory`, `test_resume_after_app_restart_preserves_secrets_and_phase`, and `test_game_end_reveals_roles_only_after_terminal_state`.

- [ ] **Step 2: Run the end-to-end tests and confirm any gaps**

Run: `python -m pytest backend/tests/e2e -q`  
Expected: first run identifies incomplete transitions or incorrect end conditions; no test may be skipped to declare completion.

- [ ] **Step 3: Fix integration gaps and write the learning README**

Use the failing end-to-end trace to repair Domain, Agent, graph, projection or UI integration. Document exact PowerShell commands and how one public talk turn and one private night action traverse the system.

- [ ] **Step 4: Run the full automated verification suite**

Run: `python -m pytest backend/tests -q`, `pnpm --dir frontend test -- --run`, and `pnpm --dir frontend build`  
Expected: PASS with both team-win paths, all 22 role behavior tests, checkpoint recovery, privacy tests, frontend tests and production build.

- [ ] **Step 5: Run both servers and play through the UI**

Start the backend with `scripts/run_backend.ps1` and the frontend with `pnpm --dir frontend dev --host 127.0.0.1`. In a browser, create an 8-seat local-mode game, act through day and night, refresh mid-game, finish the game and confirm terminal role reveal. Repeat after fixing any defect.

- [ ] **Step 6: Commit only Task 10 files**

Commit message: `docs: document and verify complete local game`.

---

## Plan Self-Review

- **Spec coverage:** All 22 Trouble Brewing roles are represented across catalogue/setup, information/registration, night, day/victory and Agent visibility tests. Player counts, Baron, the Drunk's false out-of-play Townsfolk identity and inactive ability, Spy/Recluse registration while dead, evil-team knowledge, Spy Grimoire, human action interrupts, SQLite restart, SSE and Vue client requirements map to explicit tasks. Both team wins and full UI flow are in Task 10.
- **Step clarity:** Each task has named failing tests, a focused implementation deliverable, a passing verification command and a path-limited commit. No product code is embedded in this plan.
- **Interface consistency:** `GameState`, `PlayerState`, `CharacterDefinition`, `RuleResult`, `PlayerContext`, `AgentDecision`, `GameGraphState`, `PlayerCommand`, `GameView` and `GameEvent` are introduced before consumers; application services use only graph and domain interfaces.
- **Review focus:** The five highest-risk classes each name their owning task and test coverage above.
- **Proportion:** Ten tasks preserve meaningful review boundaries across a full client/server/22-role application; each role engine, agent, graph, API and frontend can be rejected and corrected independently.
