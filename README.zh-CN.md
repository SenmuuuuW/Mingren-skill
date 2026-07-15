<div align="center">

# 🧠 名人教你 Skill

**用名人的思维方式教所有学科。**

[English](README.md) | 中文

![License](https://img.shields.io/badge/license-MIT-2ea44f)
![Markdown only](https://img.shields.io/badge/format-Markdown--only-111111)
![AI Skill](https://img.shields.io/badge/type-AI%20Skill-2563eb)
![Distilled lenses](https://img.shields.io/badge/method-distilled%20thinker%20lenses-d97706)
![MVP](https://img.shields.io/badge/MVP-4%20thinkers-7c3aed)

</div>

## ✨ 这是什么？

名人教你 Skill 是一个跨学科学习 Skill。它用经过蒸馏的思想家镜头解释真实的学术概念。

用户可以这样问：

- “老子教我微积分。”
- “费曼教我线性代数。”
- “苏格拉底追问我这道题。”
- “冯诺伊曼拆解机器学习。”

它不是假装名人聊天，而是从可靠的公开材料中提炼他们有教学价值的思考方式、解释结构、提问方法和知识立场，再把这些方法用于现代学科。

> 镜头决定通往理解的路径，但不能替代学术事实。

## 🧩 它和普通 Tutor / 角色扮演有什么不同？

| 普通 AI Tutor | 名人教你 Skill |
| --- | --- |
| 用通用方式解释 | 用指定思想家的思维方式组织解释 |
| 可能直接给出答案 | 用镜头特有的步骤引导理解 |
| 容易复制人物口吻 | 蒸馏推理方法和教学结构 |
| 可能以角色扮演为主 | 始终以学习效果为主 |
| 把风格当作装饰 | 让风格对应可复用的思维操作 |

它不是名人聊天机器人、人格模拟器或名言生成器。

## 🧠 首发四个镜头

V0.1 有意只支持四个镜头：

| 镜头 | 适合什么 | 教学方式 |
| --- | --- | --- |
| 费曼 | 小白入门、公式、抽象 STEM 概念 | 白话、类比、直觉、具体例子、小检查 |
| 冯诺伊曼 | CS、AI、系统、算法 | 输入、输出、状态、规则、模型、模块结构 |
| 苏格拉底 | 定义、证明、推理 | 追问、假设、反例、矛盾、引导发现 |
| 老子 | 变化、关系、抽象直觉 | 有/无、动/静、反向、平衡、变化 |

每个镜头都明确记录了来源基础、适用范围、薄弱场景、回答步骤和常见失败方式。

## 🚀 怎么用？

```text
费曼教我梯度下降
老子教我微积分
用苏格拉底方式问我什么是“基”
用冯诺伊曼方式拆解神经网络
```

一个典型回答只在开头点明一次镜头，随后解释真正的学术概念，给出一个小例子，并以一个检查问题或下一步结束。

## 🔍 回答流程

```text
用户问题
    ↓
识别学科、主题和学习意图
    ↓
识别或澄清人物镜头
    ↓
使用蒸馏后的思维方式解释
    ↓
回到现代学术概念
    ↓
给一个小例子
    ↓
问一个聚焦的检查问题
```

用户直接点名时，以点名为准。鲜明的方法请求可以触发对应镜头。学科本身不能自动决定镜头；如果请求含糊，就使用中性教学方式，或者只问一个真正有必要的澄清问题。

## 🧭 设计原则

- **正确性优先。** 人物风格不能覆盖标准定义、证据、机制和符号。
- **方法重于口吻。** 使用可观察的思维步骤，而不是古风、台词或表演。
- **例子小而完整。** 一个能被彻底检查的小例子胜过许多含糊类比。
- **先找卡点。** 根据用户已经表达的困惑教学，不擅自构造复杂画像。
- **只给一个下一步。** 用检查问题判断核心理解是否发生迁移。
- **边界说清楚。** 标明类比的限度和历史材料的不确定性。

## 📚 文件说明

- [`README.md`](README.md)：英文项目首页
- [`README.zh-CN.md`](README.zh-CN.md)：中文项目首页
- [`SKILL.md`](SKILL.md)：核心行为规范、镜头选择和回答流程
- [`references/distillation-framework.md`](references/distillation-framework.md)：把思想家蒸馏成教学镜头的统一标准
- [`references/trigger-framework.md`](references/trigger-framework.md)：点名、风格、意图、学科建议和歧义处理规则
- [`references/response-framework.md`](references/response-framework.md)：默认六步回答结构
- [`references/safety-boundaries.md`](references/safety-boundaries.md)：身份、来源、正确性和高风险主题边界
- [`references/thinkers/`](references/thinkers/)：四个首发人物镜头的详细说明
- [`examples/`](examples/)：中文优先的完整示例和正反对照
- [`evals/`](evals/)：质量评分表与失败分类
- [`MAINTENANCE.md`](MAINTENANCE.md)：维护范围和新增内容规则
- [`CHANGELOG.md`](CHANGELOG.md)：版本变更记录
- [`LICENSE`](LICENSE)：MIT 开源许可

## 🗂️ 仓库结构

```text
Mingren-skill/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── CHANGELOG.md
├── MAINTENANCE.md
├── LICENSE
├── references/
│   ├── distillation-framework.md
│   ├── trigger-framework.md
│   ├── response-framework.md
│   ├── safety-boundaries.md
│   └── thinkers/
├── examples/
└── evals/
```

V0.1 是一个 Markdown-first 版本，没有网站、包管理、API、后端、数据库、隐藏记忆或检索系统。

## 🛡️ 边界

- 不假装自己是名人，不说“我是费曼”
- 不伪造名言、引文、出处或历史观点
- 不使用大段受版权保护的原文
- 不为了人物风格牺牲学术正确性
- 不用玄学、诗意或戏剧表演替代真实解释
- V0.1 不模仿在世人物或私人个体
- 不建设数据库、RAG、后端或人物市场
- V0.1 不增加首发四人之外的镜头

完整规则见[安全与质量边界](references/safety-boundaries.md)。

## 🔖 当前状态

本仓库是聚焦后的 `v0.1.0` MVP。镜头质量和行为边界优先于人物数量。

## 🐍 后续代码方向

这个项目后续会在明确规划的新版本中加入代码，**计划使用 Python 作为实现语言**。当前 `v0.1.0` 仍然只包含文档，因此暂时不需要 Python、包配置或运行时依赖。

## 📄 License

本项目使用 [MIT License](LICENSE)。
