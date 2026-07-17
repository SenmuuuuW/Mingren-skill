<div align="center">

# 🧠 名人教你 Skill

<p><strong>用名人的思维方式教所有学科。</strong></p>
<p><sub>Famous Teacher Skill · Teach any subject through distilled thinker lenses.</sub></p>

<p><a href="README.md">English</a> &nbsp;|&nbsp; 中文</p>

<p>
  <a href="CHANGELOG.md"><img alt="阶段：V0.1 实验版" src="https://img.shields.io/badge/stage-v0.1%20experimental-0f766e?style=flat-square"></a>
  <a href="SKILL.md"><img alt="规范优先" src="https://img.shields.io/badge/approach-specification%20first-2563eb?style=flat-square"></a>
  <a href="pyproject.toml"><img alt="Python 3.11+ 原型" src="https://img.shields.io/badge/Python-3.11%2B%20prototype-3776AB?style=flat-square&logo=python&logoColor=white"></a>
  <a href="references/thinkers/"><img alt="四个思想家镜头" src="https://img.shields.io/badge/thinker%20lenses-4-7c3aed?style=flat-square"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square"></a>
</p>

</div>

> [!IMPORTANT]
> **当前阶段：V0.1 基础版，文档优先，实验阶段。** 教学行为、质量边界、示例和评测以 Markdown/YAML 规范为主；仓库另含范围明确的离线 Python 路由、验证、评测辅助与实验性 bundle 构建工具。

## 这个项目是什么

名人教你（Mingren Skill）是一个面向兼容 Host 执行的跨学科学习 Skill。它用四种有明确边界的思想家镜头组织解释。加载 Skill 的 Host 模型直接生成最终回答；Mingren 不调用外部模型 API。

生成后的 bundle 面向具备相应能力的 Host 环境；当前构建和验证过程仍需要 Python 及文档列出的依赖。项目尚未完成对某个具体 Host 的正式兼容性验证，也尚未实际运行人工 Host 行为评测。bundle 生成后，兼容 Host 可以在不使用本项目 Python 构建工具的情况下读取它。

名人教你 Skill 是一个跨学科学习项目。它把有公开依据的思考方式和教学方法蒸馏成明确、可检查的人物镜头，让镜头改变解释的组织方式，同时始终以真实学术概念为准。

它以学习为中心，不做名人模拟：不冒充人物、不伪造名言，也不进行戏剧化角色扮演。

## 它为什么不同

| 通用 AI Tutor | 名人教你 Skill |
| --- | --- |
| 用一般方式解释 | 用指定思想家镜头组织教学 |
| 可能模仿人格或口吻 | 蒸馏推理模式和教学动作 |
| 容易直接跳到答案 | 沿镜头特有的路径建立理解 |
| 可能把风格当成产品 | 始终把正确性和学习效果放在首位 |

## V0.1 的四个镜头

| 镜头 | 更适合什么 | 教学方式 |
| --- | --- | --- |
| 费曼 | 直觉、STEM 基础、公式 | 白话、类比、具体例子、解释回放检查 |
| 冯诺伊曼 | CS、AI、系统、算法 | 输入、参数、状态、规则、输出、模块结构 |
| 苏格拉底 | 定义、证明、推理 | 追问、假设、反例、引导发现 |
| 老子 | 抽象概念、变化、关系 | 对照、反转、平衡、关系、变化 |

V0.1 有意只支持这四个镜头。每个镜头都记录了来源基础、优势、薄弱场景、回答结构和失败风险。

## 试试这些交互

```text
用费曼镜头教我梯度下降。
用苏格拉底方式追问我这道证明题，先不要揭晓答案。
把操作系统进程调度拆成输入、状态、规则和输出。
用老子镜头打开微积分的直觉，再回到正式数学。
```

按照 Skill 规范生成的回答会先点明镜头，再解释真实概念，给出一个小例子，并以一个聚焦的检查问题或下一步结束。

## 设计中的回答流程

```text
用户问题
    ↓
识别主题和学习意图
    ↓
识别或澄清人物镜头
    ↓
应用蒸馏后的教学方式
    ↓
回到真实学术概念
    ↓
给一个小例子
    ↓
问一个聚焦的检查问题
```

用户直接指定镜头时，以指定为准。鲜明的方法请求可以建议镜头；学科本身不会自动选择镜头。“讲简单点”这类通用请求在没有明确镜头意图时保持中性。仅请求名言、归属或来源也保持中性，除非用户另行要求通过该镜头教学。

## 项目分层

| 层级 | 作用 | 关键路径 |
| --- | --- | --- |
| 产品规范 | 权威的 Skill 行为和质量边界 | [`SKILL.md`](SKILL.md)、[`references/`](references/) |
| 人物研究 | 四个镜头的来源约束与详细定义 | [`references/thinkers/`](references/thinkers/) |
| 示例与评测 | 标准示例、评测案例和失败检查 | [`examples/`](examples/)、[`evals/`](evals/) |
| Python 实现与维护工具 | 路由、离线提示预览、确定性检查、评测辅助与 bundle 构建 | [`src/mingren_skill/`](src/mingren_skill/)、[`scripts/`](scripts/)、[`tests/`](tests/) |

产品 Markdown 仍然是权威定义。实现和规范不一致时，应同步更新 Python 规则、评测案例和测试，使其重新符合规范。

## 📦 构建实验性 bundle

构建和验证 bundle 需要 Python 3.11 或更高版本、PyYAML 以及开发依赖：

```bash
python -m pip install -e ".[dev]"
python scripts/validate.py
python scripts/build_skill_bundle.py
```

命令会按确定性规则生成 `dist/skill/` 和 `dist/mingren-skill.zip`。该 bundle 格式目前属于实验性设计，面向能够加载 Markdown/YAML、保留相对引用并以 `SKILL.md` 为入口指令的 Host。项目尚未验证任何具名 Host 的兼容性。详见[实验性安装流程](docs/installation.md)和[运行时合约](docs/runtime_contract.md)。

示例请求：

```text
用简单的话解释递归。
这里的“理解”到底是什么意思？
把一个复杂的软件系统拆成模块。
```

运行时包含入口 Skill、manifest、触发、回答与安全规则、四个镜头说明、精选示例、质量指南和校验和。不支持的思想家不会被自动创建成新镜头。

## 🐍 Python 实现与维护工具

Python 包是辅助参考实现，包括确定性路由、离线提示预览、回答验证、评测辅助和开发 CLI。阅读并应用 Markdown 规范不依赖该包；构建和验证生成后的 bundle 目前仍需要文档列出的 Python 环境。兼容 Host 通常直接读取 Skill，不需要传递 `PromptPackage`。

新增 Python 工作仍受 [`MAINTENANCE.md`](MAINTENANCE.md) 中经项目所有者批准的窄范围离线工具政策约束；这不代表可以加入 Provider 集成或应用基础设施。

```text
用户请求
    ↓
语言检测、规则路由与安全判断
    ↓
EngineResult（结构化教学计划）
    ↓
离线 PromptBuilder 预览与 ResponseValidator 检查
```

工具包本身**不会**生成回答、核验事实、调用模型或提供托管 API，也不会替代宿主执行的 Skill。安全和回答检查是确定性的第一版，不是完整的专业分类器。

当前路由已经覆盖测试过的英文和中文类别，包括明确的镜头请求，以及对普通“讲简单点”请求的中性回退。模式匹配仍然基于词语而非语义，因此还不能覆盖所有别名和改写方式。

环境要求：Python 3.11 或更高版本；运行时依赖 PyYAML，开发检查使用 pytest。

```bash
python -m pip install -e ".[dev]"
python scripts/validate.py
pytest
```

CLI 提供三个明确命令：

```bash
mingren-skill plan "用简单的话解释递归"
mingren-skill prompt "这里的理解到底是什么意思？"
mingren-skill validate-response "我胸口剧痛而且无法呼吸" --response "顺其自然，先观察一下。"
```

`plan` 输出 `EngineResult`；`prompt` 输出供离线检查的 `PromptPackage`；`validate-response` 对已有回答做确定性结构与安全检查。为了向后兼容，`mingren-skill "输入"` 仍等同于 `plan`。工具包不生成用户回答，不调用模型，也不能保证事实正确。

当前限制：只支持四个镜头；离线路由依赖显式规则；验证器不能证明事实正确；bundle 格式仍处于实验阶段；尚未验证任何具名 Host 的兼容性；人工 Host 行为评测尚未实际运行；`TODO-SOURCE` 项仍是临时资料缺口。

## 文档导航

- [`SKILL.md`](SKILL.md)：核心行为规范和回答流程
- [`skill-manifest.yaml`](skill-manifest.yaml)：运行时文件、能力、版本和离线要求
- [`docs/runtime_contract.md`](docs/runtime_contract.md)：权威宿主执行合约
- [`docs/installation.md`](docs/installation.md)：实验性 bundle 的构建与加载流程
- [`references/distillation-framework.md`](references/distillation-framework.md)：蒸馏人物镜头的统一标准
- [`references/trigger-framework.md`](references/trigger-framework.md)：触发优先级、歧义与非触发规则
- [`references/response-framework.md`](references/response-framework.md)：默认教学回答结构
- [`references/safety-boundaries.md`](references/safety-boundaries.md)：身份、来源、正确性和高风险主题边界
- [`references/thinkers/`](references/thinkers/)：四个首发镜头的详细规范
- [`references/trigger_rules.yaml`](references/trigger_rules.yaml)：可执行规则、优先级、退出条件和来源链接
- [`examples/`](examples/)：中文优先的标准示例与正反对照
- [`evals/`](evals/)：人工质量检查和机器评测案例
- [`evals/host_cases.yaml`](evals/host_cases.yaml)：不调用 API 的宿主行为样例
- [`evals/prompt_snapshots/`](evals/prompt_snapshots/)：代表性的提示词回归预期
- [`docs/requirements_traceability.md`](docs/requirements_traceability.md)：产品要求到行为、测试和缺口的映射
- [`docs/behavior_alignment_review.md`](docs/behavior_alignment_review.md)：真实提示词行为审计和已确认限制
- [`AGENTS.md`](AGENTS.md)：代码代理贡献规则
- [`MAINTENANCE.md`](MAINTENANCE.md)：范围与维护规则
- [`CHANGELOG.md`](CHANGELOG.md)：版本记录

## 边界

- 不冒充人物，不声称“我是费曼”
- 不伪造名言、引文、出处或历史观点
- 不为了镜头风格牺牲正确性，不用玄学替代解释
- V0.1 不模仿在世人物或私人个体
- 不包含隐藏记忆、数据库、RAG、托管 API 或后端服务
- V0.1 不增加首发四人之外的镜头

完整规则见[安全与质量边界](references/safety-boundaries.md)。

## License

本项目使用 [MIT License](LICENSE)。
