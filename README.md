# 🤖 Agent SKILL — 终端交互式 AI 智能体

一个基于 **DeepSeek Chat** 的终端交互式 AI 助手，支持可扩展的 **技能（Skill）** 系统。用户通过命令行与 AI 对话，AI 可动态调用注册的技能来执行天气查询、时间获取、文件管理、对话历史分析等任务。

---

## ✨ 特性

- **💬 终端交互** — 直接在命令行中与 AI 对话，支持 `/help`、`/skills` 等便捷命令
- **🧩 可扩展技能系统** — 基于抽象基类 [`SkillBase`](skill/skill_base.py) 和注册表 [`SkillRegistry`](skill/skill_registry.py) 的插件式架构，新增技能只需编写一个 Python 类
- **🔧 内置技能** — 天气查询、时间获取、文件管理、对话历史分析、Token 计数等
- **📝 对话持久化** — 每次对话自动保存为 JSON 文件到 [`conversations/`](conversations/) 目录
- **📊 Token 用量追踪** — 实时显示当前会话的 Token 使用百分比
- **🪟 Windows 原生支持** — 提供 [`run_agent.bat`](run_agent.bat) 一键启动脚本

---

## 🚀 快速开始

### 环境要求

- Python 3.7+
- `openai` 库
- `requests` 库

### 安装

```bash
# 克隆项目
git clone https://github.com/DaKeXiaoLe/agent_skill.git
cd agent-skill

# 安装依赖
pip install openai requests
```

### 启动

**方式一：双击启动脚本（Windows）**

双击 [`run_agent.bat`](run_agent.bat) 即可启动。

**方式二：命令行启动**

```bash
python main.py
```

启动后你将看到如下界面：

```
============================================================
🤖 deepseek-chat 智能体 v1.0
============================================================
会话ID: session_20260512_033635
已加载 6 个可用技能
输入 /help /h 查看可用命令
输入普通文本与AI对话
对话将保存到: conversations/session_20260512_033635.json
============================================================
```

---

## ⌨️ 命令

| 命令 | 别名 | 说明 |
|------|------|------|
| `/help` | `/h` | 显示帮助信息 |
| `/exit` | `/quit`, `/q` | 退出程序 |
| `/skills` | — | 列出所有已注册的技能 |
| `/clear` | — | 清除当前对话历史（保留系统提示） |
| `/history` | — | 显示当前会话的对话历史 |
| `/reset` | — | 重置对话（清空历史，保留系统提示） |

---

## 🧩 技能系统

### 架构

技能系统采用 **注册表模式**，核心组件：

| 组件 | 文件 | 说明 |
|------|------|------|
| [`SkillBase`](skill/skill_base.py) | 抽象基类 | 定义技能的接口规范（`execute`、`validate_params`、`to_tool_dict`） |
| [`SkillRegistry`](skill/skill_registry.py) | 全局注册表 | 管理技能的注册、查找、创建 |
| [`SkillResult`](skill/skill_base.py) | 结果封装 | 统一技能执行结果的返回格式 |

### 内置技能

| 技能 | 文件 | 功能 |
|------|------|------|
| 🌤️ `get_weather_by_city` | [`skill/get_weather_by_city.py`](skill/get_weather_by_city.py) | 查询指定城市的实时天气 |
| 🕐 `get_local_time` | [`skill/get_local_time.py`](skill/get_local_time.py) | 获取指定时区或城市的当前时间 |
| 📋 `get_chat_history` | [`skill/get_chat_history.py`](skill/get_chat_history.py) | 读取并分析历史对话记录，支持日期筛选和 AI 总结 |
| 📊 `token_counter` | [`skill/token_counter.py`](skill/token_counter.py) | 统计对话 Token 数量，显示使用百分比 |
| 📁 `document_manager` | [`skill/document_manager.py`](skill/document_manager.py) | 创建、读取、更新、删除任意文件 |
| 📄 `process_resume` | — | 简历处理技能（预留扩展） |

### 创建自定义技能

参考 [`skill/creat_skill.md`](skill/creat_skill.md) 文档，只需三步：

1. **创建技能文件** — 在 [`skill/`](skill/) 目录下新建 `.py` 文件，继承 [`SkillBase`](skill/skill_base.py)
2. **实现 `execute` 方法** — 编写核心业务逻辑
3. **注册技能** — 在 [`skill/__init__.py`](skill/__init__.py) 中添加导入和注册代码

示例模板：

```python
"""my_skill - 技能描述"""
from .skill_base import SkillBase, SkillResult

class my_skill(SkillBase):
    def __init__(self):
        super().__init__(
            name="my_skill",
            description="技能功能描述"
        )
        self.parameters = {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "参数描述"
                }
            }
        }
        self.required = ["param1"]

    def execute(self, **kwargs) -> SkillResult:
        if not self.validate_params(**kwargs):
            return SkillResult(success=False, content="缺少必需参数")
        param1 = kwargs.get("param1")
        try:
            result = f"处理结果: {param1}"
            return SkillResult(success=True, content=result)
        except Exception as e:
            return SkillResult(success=False, content=f"执行失败: {str(e)}")
```

---

## 📁 项目结构

```
├── main.py                          # 主程序入口
├── run_agent.bat                    # Windows 一键启动脚本
├── temp_token_count.py              # Token 计数测试脚本
├── README.md                        # 本文件
├── skill/                           # 技能包
│   ├── __init__.py                  # 技能注册入口
│   ├── skill_base.py                # 技能抽象基类
│   ├── skill_registry.py            # 技能注册表
│   ├── token_counter.py             # Token 计数技能
│   ├── document_manager.py          # 文件管理技能
│   ├── get_chat_history.py          # 对话历史技能
│   ├── get_local_time.py            # 时间获取技能
│   ├── get_weather_by_city.py       # 天气查询技能
│   ├── creat_skill.md               # 创建技能开发文档
│   └── tokenizer/                   # 本地 Tokenizer 模型
│       ├── tokenizer.json
│       └── tokenizer_config.json
├── conversations/                   # 对话历史存储目录（自动生成）
├── documents/                       # 文档存储目录
│   ├── 笔记本.json
│   ├── 待办事宜.json
│   └── 个人信息.md
└── .vscode/                         # VS Code 配置
```

---

## ⚙️ 配置

### 修改 AI 模型

在 [`main.py`](main.py:25) 中修改 `self.model` 的值：

```python
self.model = "deepseek-chat"  # 可替换为其他兼容模型
```

### 修改 API 地址

在 [`main.py`](main.py:28) 中修改 `base_url`：

```python
self.client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.deepseek.com",  # 替换为你的 API 地址
)
```

### Token 限制

在 [`skill/token_counter.py`](skill/token_counter.py:44) 中修改 `self.token_limit`：

```python
self.token_limit = 128000  # 默认 128K，可根据模型调整
```

---

## 📜 对话存储

每次启动都会创建一个新的会话，对话记录以 JSON 格式保存在 [`conversations/`](conversations/) 目录下，文件名为 `session_YYYYMMDD_HHMMSS.json`。

示例结构：

```json
{
  "session_id": "session_20260512_033635",
  "created_at": "2026-05-12T03:36:35",
  "messages": [
    { "role": "system", "content": "..." },
    { "role": "user", "content": "今天天气怎么样？" },
    { "role": "assistant", "content": "..." }
  ],
  "message_count": 3
}
```

---

## 🛠️ 技术栈

- **Python 3** — 核心开发语言
- **OpenAI SDK** — 兼容 DeepSeek Chat API
- **Transformers** — 本地 Tokenizer 加载（可选）
- **Requests** — HTTP 请求（天气查询）

---

## 📄 许可证

[MIT](LICENSE)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来扩展技能或改进功能！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-skill`)
3. 提交更改 (`git commit -m 'Add amazing skill'`)
4. 推送到分支 (`git push origin feature/amazing-skill`)
5. 创建 Pull Request
