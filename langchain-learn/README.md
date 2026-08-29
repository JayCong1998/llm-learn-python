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
