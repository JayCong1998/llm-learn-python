# 从独立模块导入六个编程工具。
from agents.coding_tools.bash import Bash
from agents.coding_tools.edit import Edit
from agents.coding_tools.glob import Glob
from agents.coding_tools.grep import Grep
from agents.coding_tools.read import Read
from agents.coding_tools.write import Write

# 汇总供 Agent 绑定的编程工具。
coding_tools = [Read, Glob, Grep, Edit, Write, Bash]
