<div align="center">

# 🧠 名人教你 Skill

<p><strong>用名人的思维方式教所有学科。</strong></p>
<p><sub>Famous Teacher Skill · Teach any subject through distilled thinker lenses.</sub></p>

<p><a href="README.md">English</a> &nbsp;|&nbsp; 中文</p>

<p>
  <a href="CHANGELOG.md"><img alt="阶段：V0.1 基础版" src="https://img.shields.io/badge/stage-v0.1%20foundation-0f766e?style=flat-square"></a>
  <a href="SKILL.md"><img alt="规范优先" src="https://img.shields.io/badge/approach-specification%20first-2563eb?style=flat-square"></a>
  <a href="pyproject.toml"><img alt="Python 3.11+ 原型" src="https://img.shields.io/badge/Python-3.11%2B%20prototype-3776AB?style=flat-square&logo=python&logoColor=white"></a>
  <a href="references/thinkers/"><img alt="四个思想家镜头" src="https://img.shields.io/badge/thinker%20lenses-4-7c3aed?style=flat-square"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square"></a>
</p>

</div>

> [!IMPORTANT]
> **当前阶段：V0.1 基础版。** 教学行为、质量边界、示例和评测仍然以 Markdown 规范为主。仓库中也已经有一个早期、确定性的 Python 实现，用于路由、生成模型可用的提示词包，以及检查候选回答；它还不是完整的答案生成产品。

## 这个项目是什么

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

用户直接指定镜头时，以指定为准。鲜明的方法请求可以建议镜头；学科本身不会自动选择镜头。“讲简单点”这类通用请求在没有明确镜头意图时保持中性。

## 项目分层

| 层级 | 作用 | 关键路径 |
| --- | --- | --- |
| 产品规范 | 权威的 Skill 行为和质量边界 | [`SKILL.md`](SKILL.md)、[`references/`](references/) |
| 人物研究 | 四个镜头的来源约束与详细定义 | [`references/thinkers/`](references/thinkers/) |
| 示例与评测 | 标准示例、评测案例和失败检查 | [`examples/`](examples/)、[`evals/`](evals/) |
| Python 原型 | 路由、提示词打包和确定性回答检查 | [`src/mingren_skill/`](src/mingren_skill/)、[`tests/`](tests/) |

产品 Markdown 仍然是权威定义。实现和规范不一致时，应同步更新 Python 规则、评测案例和测试，使其重新符合规范。

## Python 实现原型

Python 是当前的实现方向。这个包把产品规则分成四个可检查阶段：

```text
用户请求
    ↓
语言检测、规则路由与安全判断
    ↓
EngineResult（结构化教学计划）
    ↓
PromptBuilder → PromptPackage（system/developer/user 提示词）
    ↓
由集成方选择的外部模型服务（本仓库不包含）
    ↓
候选学习回答
    ↓
ResponseValidator → 问题列表与修改要求
```

这个原型本身**不会**生成回答、核验事实、调用外部模型或提供托管 API，也不是已经完成的教学应用。安全和回答检查都是确定性的第一版，并不是完整的专业分类器；后续仍有大量实际实现工作。

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

`plan` 输出 `EngineResult`；`prompt` 输出与模型供应商无关的 `PromptPackage`；`validate-response` 报告确定性问题和修改要求。为了向后兼容，`mingren-skill "输入"` 和 `python -m mingren_skill "输入"` 仍等同于 `plan`。

当前不包含模型供应商 SDK、网络调用、流式输出或 API 密钥处理。

## 文档导航

- [`SKILL.md`](SKILL.md)：核心行为规范和回答流程
- [`references/distillation-framework.md`](references/distillation-framework.md)：蒸馏人物镜头的统一标准
- [`references/trigger-framework.md`](references/trigger-framework.md)：触发优先级、歧义与非触发规则
- [`references/response-framework.md`](references/response-framework.md)：默认教学回答结构
- [`references/safety-boundaries.md`](references/safety-boundaries.md)：身份、来源、正确性和高风险主题边界
- [`references/thinkers/`](references/thinkers/)：四个首发镜头的详细规范
- [`references/trigger_rules.yaml`](references/trigger_rules.yaml)：可执行规则、优先级、退出条件和来源链接
- [`examples/`](examples/)：中文优先的标准示例与正反对照
- [`evals/`](evals/)：人工质量检查和机器评测案例
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

## 后续方向

近期目标是让 Skill 规范、来源边界、评测案例、提示词快照和 Python 原型保持一致。后续实现可以接入模型供应商并继续走向更完整的学习体验，同时不削弱正确性、出处约束和四镜头范围。

## License

本项目使用 [MIT License](LICENSE)。
