from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# 从.env文件中加载环境变量
load_dotenv(override=True)

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")
QWEN_MODEL = os.getenv("QWEN_MODEL")

model = ChatOpenAI(
    model=QWEN_MODEL,
    api_key=DASHSCOPE_API_KEY,
    base_url=QWEN_BASE_URL
)

def call(query: str) -> str:
    response = model.invoke([HumanMessage(content=query)])
    return response.content
