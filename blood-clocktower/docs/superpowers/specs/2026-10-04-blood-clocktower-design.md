# 血染钟楼多智能体游戏设计

**状态：** 待用户审阅

**日期：** 2026-10-04

## 目标

构建一个本地可运行的血染钟楼游戏：一名人类玩家与多名 AI 玩家进行完整的 Trouble Brewing 对局。每个 AI 座位是独立的玩家 Agent，拥有自己的角色、阵营、私有信息和发言策略。后端以 LangChain 提供模型接入、以 LangGraph 编排可暂停和恢复的游戏状态；前端采用 Vue 3、TypeScript、Vite、Vue Router 和 Pinia。

项目面向希望学习 LangChain 与 LangGraph 的开发者，因此模块边界、数据流、图状态和启动方式都要在 README 中说明。游戏规则由确定性的领域层执行，模型负责玩家表达和策略选择。

## 范围与默认值

- 支持 5 至 15 个座位，其中恰有 1 名人类玩家，其余座位由各自独立的 AI Agent 扮演；默认创建 8 人局。
- 支持 Trouble Brewing 全部 22 个角色：Washerwoman、Librarian、Investigator、Chef、Empath、Fortune Teller、Undertaker、Monk、Ravenkeeper、Virgin、Slayer、Soldier、Mayor、Butler、Drunk、Recluse、Saint、Poisoner、Spy、Scarlet Woman、Baron、Imp。按标准玩家人数表抽取阵营类别，再由规则引擎处理 Baron 等设置阶段的角色数量变化。每局角色随机分配并对玩家保密，避免固定阵容泄露身份。
- 覆盖标准身份与阵营信息、首夜信息、每晚行动、公开讨论、提名、投票、处决、死亡投票标记、角色被动能力、信息错误状态、胜利判定和结束后的完整身份揭示。
- 第一版只实现 Trouble Brewing，不含其他剧本、旅行者、自定义角色、联网多人、帐号系统和主持人配置界面。
- 游戏状态和 LangGraph checkpoint 保存在本机 SQLite。应用重启后可继续尚未结束的对局；同一实例内可创建多个独立游戏。生产运行的随机种子由服务端生成并保密，只有规则测试可注入固定种子。
- LLM 通过环境变量配置 OpenAI 兼容接口。没有密钥时使用明确标注的本地策略模式，让规则和前后端流程仍可完整运行；本地模式不冒充语言模型生成能力。
- checkpoint 依赖至少使用 `langgraph>=1.0.10`、`langgraph-checkpoint>=4.1.1` 和 `langgraph-checkpoint-sqlite>=3.0.1`，并在 LangGraph 导入前开启 `LANGGRAPH_STRICT_MSGPACK=true`；安装时生成锁文件以固定可复现的兼容依赖。

## 玩法依据与规则边界

官方规则将游戏分为白天和夜晚：白天讨论并提名，夜晚触发部分角色能力；好人阵营在恶魔死亡时获胜，邪恶阵营在只剩两名存活玩家时获胜。被处决者需获得至少半数存活玩家的票数，并且票数高于其他被提名者；未达门槛或最高票平票时不处决。死亡玩家仍可发言，并保留一次投票机会。醉酒或中毒会令角色能力失效，同时允许 Storyteller 提供错误信息。[Rules Explanation](https://wiki.bloodontheclocktower.com/Rules_Explanation) [States](https://wiki.bloodontheclocktower.com/States)

Trouble Brewing 是官方推荐给新玩家的入门剧本，包含 13 名镇民、4 名外来者、4 名爪牙和 Imp 恶魔。规则资料说明至少 5 人开局，人数配置按 5 至 15 人表确定；Baron 在设置阶段以两名外来者替换两名镇民。[Trouble Brewing](https://wiki.bloodontheclocktower.com/Trouble_Brewing) [Setup](https://wiki.bloodontheclocktower.com/Setup) [Baron](https://wiki.bloodontheclocktower.com/Baron)

本项目使用的基础人数表（15 人以内均为 1 个恶魔）：

| 玩家人数 | 镇民 | 外来者 | 爪牙 | 恶魔 |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 3 | 0 | 1 | 1 |
| 6 | 3 | 1 | 1 | 1 |
| 7 | 5 | 0 | 1 | 1 |
| 8 | 5 | 1 | 1 | 1 |
| 9 | 5 | 2 | 1 | 1 |
| 10 | 7 | 0 | 2 | 1 |
| 11 | 7 | 1 | 2 | 1 |
| 12 | 7 | 2 | 2 | 1 |
| 13 | 9 | 0 | 3 | 1 |
| 14 | 9 | 1 | 3 | 1 |
| 15 | 9 | 2 | 3 | 1 |

游戏引擎应落实全部 22 个角色的标准能力，不让 LLM 裁决游戏规则。特殊登记信息（如 Recluse、Spy）、Drunk 的错误认知、Poisoner 的中毒、Fortune Teller 的 red herring、Virgin 首次被提名、Slayer 一次性能力、Ravenkeeper 夜间死亡触发、Scarlet Woman 接替恶魔、Imp 自刀转移、Butler 的投票限制、Saint 被处决的胜负检查、Soldier 防恶魔攻击和 Mayor 的夜间替代死亡等情况由规则服务依据角色定义处理。执行某些信息能力时，Storyteller 可提供错误信息；这类信息由独立的故事主持逻辑生成并记录其依据，不由 Agent 自行改写服务器状态。

不实现跨剧本的 Jinx、自定义脚本平衡、旅行者和其他剧本角色。每个 Trouble Brewing 角色及其标准交互都必须有独立定义与覆盖证据；无法确定的冲突应由规则层明确处理并保留事件记录，不能让模型临场发明裁定。

## 系统结构

```text
Vue 3 游戏界面
  ├─ Vue Router：开始页与对局页
  ├─ Pinia：公开局面、人类私有面板、待提交动作
  └─ API client：HTTP 命令 + SSE 游戏事件
          │
          ▼
FastAPI 接口与视图投影
          │
应用服务：创建游戏、校验座位命令、构造玩家视图
          ├─ 领域层：玩家、角色、状态、角色能力与规则裁定
          ├─ LangGraph：阶段编排、暂停等待人类输入、恢复游戏
          └─ 玩家 Agent：按座位调用 LangChain 模型或本地策略
                      │
                      ▼
             SQLite checkpoint / 对局状态
```

### 后端分层

1. **Domain（领域层）**：使用可序列化的类型描述玩家、真实角色、玩家所知角色、阵营、存活状态、醉酒/中毒状态、夜晚动作、提名、投票令牌和游戏阶段。通过纯规则函数计算允许的动作、信息结果、死亡和胜负。角色定义注册在独立模块中；规则服务根据角色与阶段分派能力。
2. **Agents（玩家智能体）**：统一 `PlayerAgent` 接口，为每个 AI 座位构造带该座位私有信息的输入。模型使用 LangChain 的 `ChatOpenAI` 兼容实现和结构化输出；本地策略遵循同一输入/输出 schema。Agent 只生成公开话语或受限动作提案，后端校验并执行动作。模型不得直接修改 Domain 状态。
3. **Gameflow（LangGraph）**：使用有类型的共享状态、职责单一的节点和显式条件边。主要阶段为设置、首夜、白天开放与公开讨论、提名与逐人投票、结算、后续夜晚、胜负检查。需要人类选择时通过 interrupt 暂停；API 将命令交给图恢复执行，直到下一次人类输入或游戏结束。使用 SQLite checkpointer 以游戏 ID 作为 thread ID 隔离状态。采用 AsyncSqliteSaver 与单进程本地部署；未来需要多实例并发时再替换为服务端数据库 checkpointer。
4. **Application / API**：应用服务负责调用图、验证命令、管理错误和将完整内部状态投影为允许用户读取的响应。FastAPI 不直接实现角色规则，也不把 checkpoint 原样返回给前端。
5. **Persistence**：LangGraph SQLite checkpointer 是对局恢复的权威状态源。图状态保留已处理 action ID 和带唯一事件 ID 的公开/私有事件记录，支持幂等恢复与 SSE 续订。通过专用 repository / projection 访问状态；秘密角色、Agent 输入和私有信息不可写入公开事件通道。

LangGraph 的 `StateGraph` 由状态、节点和边组成，并在调用前编译；图状态支持为长流程存储 checkpoint。以上职责划分用于让读者能分别理解规则、Agent 决策和流程调度。[LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)

### 玩家 Agent 的知识隔离

模型调用只接收当前发言或行动所需的上下文：公开脚本、公开对话与事件、玩家自己获知的角色与阵营、该玩家的独立记忆、已收到的私有信息及邪恶队友信息（仅适用于规则允许得知的座位）。Drunk 只会看到自己以为的 Investigator 角色，不能向它泄露服务器记录的真实 Drunk 身份。不得传入完整 Grimoire、其他 AI 的私有记录、未公开角色分配或内部裁定记录；例外是活着的 Spy 在有效夜晚按其能力获知的 Grimoire，该信息只进入 Spy 座位的私有上下文。恶魔 bluff、邪恶队伍初始信息和 Spy 视图都必须按规则阶段和角色能力定向投影。人类端点同样只显示人类实际获知的私有信息。SSE 只发送公开聊天、公开死亡/处决/阶段变化以及显式发给人类的私密信息事件。

模型输出使用 Pydantic schema 约束为 `speak`、`nominate`、`vote`、`night_action` 等有限动作。服务端验证角色、存活状态、每日次数、夜间目标和投票令牌；验证失败时请求一次修正，仍失败则走可见的安全策略并记录非敏感错误摘要。不给前端显示模型的隐藏推理或完整 prompt。

## 前后端交互

- 开始页允许填写人类玩家昵称、座位数（5–15，默认 8）和模型模式；`POST /api/games` 返回新对局 ID 与人类实际获知的角色/阵营私密信息。
- 对局页展示玩家圆桌、公开存活/死亡状态、全部 22 个脚本角色（中文名称和英文原名）、公开讨论流、白天/夜晚阶段、提名与投票控件，以及仅当前人类可见的角色能力和私有信息；进行中不显示其他人的真实阵营。
- 人类的聊天、提名、投票、夜间选择和结束讨论操作通过 `POST /api/games/{game_id}/actions` 提交；`GET /api/games/{game_id}` 返回经过过滤的公开视图及人类私有视图；`GET /api/games/{game_id}/events` 以 SSE 订阅公开事件与属于该人类的私密事件。
- 连接恢复后客户端重新读取视图并续订事件。所有动作含唯一 action ID，服务端在恢复图之前校验阶段与重复提交，以避免重连导致重复处决、投票或夜间行动。
- 游戏结束时将真实角色和阵营全部公开，提供时间线回顾；游戏进行中只有规则明确告知人类的私有信息及其角色能力允许看到的信息（例如 Spy 夜间看见的 Grimoire）可见。

## 前端职责

- Vue Router 管理开始页和 `/games/:gameId` 对局页。
- Pinia store 保存由 API 投影返回的视图状态、SSE 事件游标、错误状态和待提交动作，不保存或推断服务端未公开的真实游戏状态。
- 页面拆为游戏桌、座位卡片、公开对话、私密信息、行动面板和结束回顾组件；所有可用操作以服务端返回的 `available_actions` 为准。
- 视觉样式以桌游夜间氛围为主题，重点呈现座位、存活/死亡、公开信息与私密信息边界；不依赖外部图片资源或官方商标素材。

## 失败处理

- 无效或重复动作返回明确的 4xx 错误与允许动作列表，且不改变 checkpoint。
- LLM 超时、不可用或输出 schema 无效时记录脱敏错误，尝试有限次重试，再由同一接口的本地策略继续该席行动；前端通过公开状态提示发生了自动决策，不暴露私有 Agent 上下文。
- SQLite/checkpoint 读取或写入失败时拒绝继续推进局面，并返回可恢复的服务错误，不以内存状态覆盖持久状态。数据库只在本机使用且不入 Git；按 LangGraph SQLite checkpointer 的安全建议启用严格的 checkpoint 反序列化白名单，依赖版本需不低于上方已验证的修复版本。
- SSE 断线不回滚已完成动作；客户端以最后收到的事件 ID 续订，缺失历史时读取最新视图。
- 游戏阶段变化和公开游戏事件以事件 ID 记录，领域动作需幂等，避免浏览器重试制造重复副作用。

## 学习与开发文档

交付包含简体中文 README，说明 Python 与 Node 环境要求、安装和启动前后端命令、模型环境变量、无需密钥的本地模式、测试/验证命令、端口和常见错误。README 还要用图说明一次白天发言和一次夜晚行动分别如何经过 API、LangGraph、PlayerAgent、规则服务和前端投影，并指向各层源文件供逐步学习。LangGraph checkpoint 数据包含未公开角色和私有信息，只用于本机开发；启用 checkpoint SQLite 文档建议的严格反序列化白名单，并使用包含已知安全修复的依赖版本。

遵守仓库 `AGENTS.md`：每一条新增或修改的有效 Python 代码行，其前一行须有简短准确的中文独立行注释；空行、纯注释和文档字符串不需重复注释。注释不得暴露密钥或其他敏感信息。

## 验收标准

1. 能从开始页创建 5 至 15 人局；每个局有 1 名人类与其余 AI 座位，角色组成符合官方人数表，Baron 的设置效果正确，角色分配随机且人类只看到规则告知自己的身份、阵营和私有信息。
2. Trouble Brewing 的全部 22 个角色都有能力定义、有效触发阶段与领域验证；角色触发、设置修改、间接胜负效果和角色信息展示均有规则单元验证覆盖。
3. LangGraph 可从开局推进首夜，暂停等待人类行动，按命令恢复，经历讨论、提名、投票、处决和后续夜晚，并在胜负条件出现时结束。暂停、重连和恢复不得重复应用已提交动作。
4. 本地策略模式无需模型密钥即可从设置推进到完整结局；两个阵营的胜利路径均可由确定性场景走通。配置模型时，多个 AI 座位以独立私有上下文生成公开对话与行动。
5. API 和 SSE 不泄露规则未告知人类的其他座位真实角色、私密信息、提示词或隐藏推理；结束后才展示完整阵容。
6. Vue 页面可与 FastAPI 建局、订阅、提交动作、刷新恢复并显示游戏结束面板；前端生产构建成功。
7. README 能让开发者按说明启动前后端并理解 LangChain、LangGraph、规则引擎和 Vue 状态管理之间的数据流。

## 主要验证方式

- Domain：人数表、Baron 修改、信息角色、夜间行动、提名/投票阈值、死亡投票次数、醉酒/中毒、特殊触发、胜负和无效动作的单元测试。
- Agents：结构化输出通过校验、错误恢复、AI 私有上下文隔离和本地策略确定性验证。
- Gameflow：使用临时 SQLite checkpoint 验证 interrupt/resume、幂等动作、阶段循环和结局；端到端脚本分别走通好人胜利与邪恶胜利。
- API：FastAPI client 验证建局、公开/私有视图权限、动作失败不改状态、SSE 事件筛选与恢复。
- Frontend：`npm run build` 与浏览器实际操作验证建局、夜晚选择、日间发言/投票、刷新恢复和游戏结束。
- 完成前从用户视角启动两个服务，实际走完一局，并对故障修复后重复验证。

## 调研来源

- [官方 Trouble Brewing 剧本与角色列表](https://wiki.bloodontheclocktower.com/Trouble_Brewing)
- [官方 Setup 说明](https://wiki.bloodontheclocktower.com/Setup)
- [官方 Rules Explanation](https://wiki.bloodontheclocktower.com/Rules_Explanation)
- [官方 States 说明](https://wiki.bloodontheclocktower.com/States)
- [官方 Baron 规则说明](https://wiki.bloodontheclocktower.com/Baron)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph Memory 与持久化](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [LangGraph SQLite checkpoint 实现与安全建议](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint-sqlite/README.md)
- [LangGraph msgpack checkpoint 修复版本 GHSA](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-g48c-2wqr-h844)
- [LangGraph JSON checkpoint 修复版本 GHSA](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-fjqc-hq36-qh5p)
- [SQLite checkpoint 修复版本 GHSA](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-9rwj-6rc7-p77c)
- [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [规则书人数表 PDF（镜像）](https://board-game-rules.com/wp-content/uploads/2025/01/blood-on-the-clocktower_Official-Rules.pdf)
- [LangChain OpenAI 聊天模型接入](https://docs.langchain.com/oss/python/integrations/chat/openai)
- [Vue Quick Start](https://vuejs.org/guide/quick-start.html)
- [Vue Tooling 与 Vite 建议](https://vuejs.org/guide/scaling-up/tooling)
