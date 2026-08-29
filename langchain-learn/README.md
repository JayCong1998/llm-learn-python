# LangChain 学习项目

这是一个使用 LangChain 调用 OpenAI 兼容聊天模型的最小示例。

## 运行

在本目录执行：

```powershell
Copy-Item .env.example .env
# 编辑 .env，填入真实的 OPENAI_API_KEY
..\llm\Scripts\python.exe -m pip install -r requirements.txt
..\llm\Scripts\python.exe main.py
```

`.env` 含有密钥，已被 Git 忽略，不能提交。

## 提示词工程示例

完成上述配置后，在本目录运行：

```powershell
..\llm\Scripts\python.exe -m prompt_engineering.main
```

该命令会使用同一份 OpenAI 兼容模型配置，依次调用下列提示词工程 API：

| API | 演示内容 |
| --- | --- |
| `PromptTemplate` | 使用命名变量创建文本提示词。 |
| `ChatPromptTemplate` | 组合 system 与 human 聊天消息。 |
| `MessagesPlaceholder` | 在聊天模板中插入历史消息。 |
| `FewShotPromptTemplate` | 使用文本格式的固定示例引导输出。 |
| `FewShotChatMessagePromptTemplate` | 使用聊天消息格式的问答示例。 |
| `LengthBasedExampleSelector` | 按提示词长度选择少样本示例。 |

示例源码位于 `prompt_engineering/`。每个构造函数只负责创建一种提示词，`app.py` 负责通过 `prompt | model` 把模板连接到模型并调用。
