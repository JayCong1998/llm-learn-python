# 导入文件系统路径类型。
from pathlib import Path

# 导入 LangChain 助手消息和可运行函数。
from langchain_core.messages import AIMessage
# 导入 LangChain 可运行函数封装。
from langchain_core.runnables import RunnableLambda
# 导入测试框架。
import pytest

# 导入本地技能异常。
from api.core.errors import InvalidResourceNameError, ResourceNotFoundError
# 导入本地技能加载与调用服务。
from api.modules.skills.service import SkillLoader, SkillService


# 定位项目内受版本控制的技能目录。
SKILLS_ROOT = Path(__file__).resolve().parents[2] / "skills"


# 验证列表只包含直接子目录中的有效技能。
def test_skill_loader_lists_valid_skills_in_name_order() -> None:
    # 创建技能加载器。
    loader = SkillLoader(SKILLS_ROOT)
    # 列出可用技能。
    skills = loader.list_skills()
    # 验证无效目录被过滤且名称排序稳定。
    assert [skill.name for skill in skills] == [
        "code-explainer",
        "text-summarizer",
    ]


# 验证非法技能名称在文件访问前被拒绝。
@pytest.mark.parametrize(
    "name",
    ["../secret", "C:\\secret", "a/b", "", "UPPER"],
)
def test_skill_loader_rejects_unsafe_names(name: str) -> None:
    # 创建技能加载器。
    loader = SkillLoader(SKILLS_ROOT)
    # 验证非法名称映射为稳定异常。
    with pytest.raises(InvalidResourceNameError):
        # 尝试加载越界名称。
        loader.load(name)


# 验证不存在的合法名称返回资源未找到。
def test_skill_loader_reports_unknown_safe_name() -> None:
    # 创建技能加载器。
    loader = SkillLoader(SKILLS_ROOT)
    # 验证合法但不存在的名称得到未找到错误。
    with pytest.raises(ResourceNotFoundError):
        # 尝试加载不存在技能。
        loader.load("missing-skill")


# 验证技能说明和用户输入使用不同消息角色。
def test_skill_service_separates_system_instructions_and_user_input(
) -> None:
    # 创建消息捕获字典。
    captured = {}

    # 定义可观察的模型响应函数。
    def respond(prompt_value):
        # 保存提示词生成的消息。
        captured["messages"] = prompt_value.to_messages()
        # 返回固定助手回答。
        return AIMessage(content="这是代码解释")

    # 创建可组合的替身模型。
    model = RunnableLambda(respond)
    # 创建本地技能服务。
    service = SkillService(loader=SkillLoader(SKILLS_ROOT), model=model)
    # 调用代码解释技能。
    result = service.invoke("code-explainer", "print('hello')")
    # 验证模型回答被返回。
    assert result.answer == "这是代码解释"
    # 验证技能正文进入系统消息。
    assert captured["messages"][0].type == "system"
    # 验证用户输入保持独立的人类消息。
    assert captured["messages"][1].content == "print('hello')"
