"""本地技能白名单加载、枚举和模型调用服务。"""

# 导入文件系统路径类型。
from pathlib import Path
# 导入正则表达式工具。
import re
# 导入通用对象和可调用类型。
from typing import Any, Callable

# 导入 LangChain 聊天提示词模板。
from langchain_core.prompts import ChatPromptTemplate
# 导入 Pydantic 数据模型。
from pydantic import BaseModel

# 导入本地资源和上游异常。
from api.core.errors import (
    InvalidResourceNameError,
    ResourceNotFoundError,
    UpstreamServiceError,
)

# 定义本地技能名称白名单格式。
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


# 定义完整本地技能对象。
class LocalSkill(BaseModel):
    # 保存技能安全名称。
    name: str
    # 保存技能简短描述。
    description: str
    # 保存 SKILL.md 完整指令。
    instructions: str


# 定义不含指令正文的技能摘要。
class SkillSummary(BaseModel):
    # 保存技能安全名称。
    name: str
    # 保存技能简短描述。
    description: str


# 定义技能调用结果。
class SkillInvokeResult(BaseModel):
    # 保存实际调用的技能名称。
    name: str
    # 保存技能描述。
    description: str
    # 保存模型回答。
    answer: str


# 定义固定根目录的本地技能加载器。
class SkillLoader:
    # 保存解析后的技能根目录。
    def __init__(self, root: Path) -> None:
        # 解析根目录以便执行边界检查。
        self.root = root.resolve()

    # 列出直接子目录中的有效技能。
    def list_skills(self) -> list[LocalSkill]:
        # 在根目录不存在时返回空列表。
        if not self.root.is_dir():
            # 返回稳定空集合。
            return []
        # 初始化有效技能列表。
        skills: list[LocalSkill] = []
        # 按目录名称稳定遍历直接子项。
        for child in sorted(self.root.iterdir(), key=lambda path: path.name):
            # 跳过非目录或不满足白名单的名称。
            if not child.is_dir() or not SKILL_NAME_PATTERN.fullmatch(child.name):
                # 继续检查下一个子项。
                continue
            # 跳过缺少固定技能文件的目录。
            if not (child / "SKILL.md").is_file():
                # 继续检查下一个子项。
                continue
            # 加载已经通过基础筛选的技能。
            skills.append(self.load(child.name))
        # 返回按名称排序的技能列表。
        return skills

    # 加载指定白名单技能。
    def load(self, name: str) -> LocalSkill:
        # 拒绝任何不符合白名单的名称。
        if not SKILL_NAME_PATTERN.fullmatch(name):
            # 抛出不回显文件系统信息的异常。
            raise InvalidResourceNameError("技能名称不合法")
        # 构造并解析固定层级技能文件路径。
        skill_file = (self.root / name / "SKILL.md").resolve()
        # 确认解析后文件仍位于技能根目录下一层。
        if skill_file.parent.parent != self.root:
            # 拒绝越过固定目录边界的路径。
            raise InvalidResourceNameError("技能名称不合法")
        # 确认技能文件真实存在。
        if not skill_file.is_file():
            # 报告稳定的未找到错误。
            raise ResourceNotFoundError("本地技能不存在")
        # 以 UTF-8 读取受控技能内容。
        instructions = skill_file.read_text(encoding="utf-8")
        # 从正文提取简短描述。
        description = extract_skill_description(instructions)
        # 返回不包含绝对路径的技能对象。
        return LocalSkill(
            name=name,
            description=description,
            instructions=instructions,
        )


# 从技能文档提取首个说明段落。
def extract_skill_description(instructions: str) -> str:
    # 按行检查技能正文。
    for line in instructions.splitlines():
        # 去除当前行首尾空白。
        stripped = line.strip()
        # 跳过空行和 Markdown 标题。
        if not stripped or stripped.startswith("#"):
            # 继续寻找说明文本。
            continue
        # 返回长度受控的首个说明行。
        return stripped[:200]
    # 为缺少说明段落的技能返回稳定文本。
    return "本地技能"


# 定义本地技能模型调用服务。
class SkillService:
    # 保存技能加载器和延迟模型来源。
    def __init__(
        self,
        loader: SkillLoader,
        model: Any = None,
        model_factory: Callable[[], Any] | None = None,
    ) -> None:
        # 保存白名单技能加载器。
        self.loader = loader
        # 保存可选的已创建聊天模型。
        self.model = model
        # 保存可选的延迟模型工厂。
        self.model_factory = model_factory

    # 列出不含指令正文的技能摘要。
    def list_skills(self) -> list[SkillSummary]:
        # 将完整技能转换为安全摘要。
        return [
            SkillSummary(name=skill.name, description=skill.description)
            for skill in self.loader.list_skills()
        ]

    # 使用指定本地技能处理用户输入。
    def invoke(self, name: str, user_input: str) -> SkillInvokeResult:
        # 在模型调用前完成名称和路径校验。
        skill = self.loader.load(name)
        # 在技能校验通过后才创建聊天模型。
        model = self.model
        # 处理尚未创建模型的服务实例。
        if model is None:
            # 确认服务配置了模型工厂。
            if self.model_factory is None:
                # 报告稳定的服务构造错误。
                raise UpstreamServiceError("本地技能模型未配置")
            # 延迟读取模型密钥和创建适配器。
            model = self.model_factory()
        # 将技能指令和用户输入保持为不同角色。
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", skill.instructions),
                ("human", "{input}"),
            ]
        )
        # 尝试调用技能提示词链。
        try:
            # 组合提示词和模型并提交用户输入。
            response = (prompt | model).invoke({"input": user_input})
        # 捕获模型执行异常。
        except Exception as error:
            # 映射为不泄露技能路径的上游错误。
            raise UpstreamServiceError("本地技能调用失败") from error
        # 返回技能元数据和模型正文。
        return SkillInvokeResult(
            name=skill.name,
            description=skill.description,
            answer=str(response.content),
        )
