---
name: fi-init
description: 通过对话收集项目需求，自动生成 requirement-template.md
trigger: /fi-init
dependencies:
  - superpowers:brainstorming
references:
  - ../shared-references/requirement-template-structure.md
---

# 需求收集 Skill

用户**无需手写需求文档**，只需提供产品/项目的粗略想法，通过对话即可自动生成 `requirement-template.md`。

## 前置条件

- 无（这是整个流程的入口）

## 功能说明

将用户碎片化或粗略的想法，通过结构化对话整理成完整的需求文档。

**核心理念**：
- 用户只需提供想法，AI 负责整理
- 一次只问一个问题，降低认知负担（来自 brainstorming）
- 提供选项加速对话，也允许自由输入
- 动态调整问题，根据项目类型定制

## 执行流程

### Step 0: 检查并安装外部依赖

在执行前，自动检查外部 Skills 是否已安装：

```bash
# 检查 superpowers plugin 是否已安装
claude /plugin | grep -i superpowers
```

如果外部依赖未安装，提示用户是否安装。选择安装则执行：

```bash
python .claude/scripts/install.py
```

### Step 1: 调用 Brainstorming

调用 `@superpowers:brainstorming` 开始需求探索：

```
@superpowers:brainstorming

目标：收集项目需求，生成 requirement-template.md

探索重点：
1. 项目目标（一句话说明）
2. 核心功能（必须有什么）
3. 非功能需求（性能、安全、技术约束）
4. 边界条件（不做什么）
5. 验收标准（怎么算完成）
```

### Step 2-8: 对话收集

按以下顺序收集信息：
1. **初步询问**：请用一两句话描述你想做什么
2. **项目类型**：全栈/后端/前端/CLI/类库/其他
3. **核心功能**：循环收集直到用户说"没有了"
4. **AI 服务**：如果涉及 AI，确认需要哪些能力
5. **技术约束**：本地部署/高并发/移动端/离线等
6. **目标用户**：个人/小团队/中型企业/大型企业
7. **汇总确认**：展示需求汇总，等待确认

### Step 9: 生成文档

用户确认后，在项目根目录生成 `requirement-template.md`。生成时须按 `.claude/shared-references/requirement-template-structure.md` 所定义的结构与必填项输出，确保含项目名称、目标、类型，至少一个核心功能（含描述、优先级、验收标准），以及至少一条整体验收标准，以便通过后续 `validate.py requirement` 校验。

### Step 10: 自动校验并完成

生成 `requirement-template.md` 后，**必须自动执行**（无需用户手动运行）：

```bash
python .claude/scripts/validate.py requirement
```

- **校验通过**：提示下一步：
  ```
  ✅ 需求文档已生成并校验通过：requirement-template.md
  下一步：/fi-plan 开始架构设计
  ```
- **校验失败**：根据脚本输出的缺失项（如缺少项目名称、目标、核心功能、验收标准）补充或修正 `requirement-template.md`，再次运行上述校验命令；若多次仍不通过，提示用户补全后重新执行 `/fi-init`。

## 询问策略

### 问题优先级

1. **必问**：项目目标、核心功能
2. **按需问**：AI 服务（如果涉及 AI）、技术约束
3. **可推断**：验收标准、边界条件（可从功能推断）

### 交互原则

- **一次一问**：不要一次问多个问题
- **提供选项**：a/b/c 加速选择
- **允许跳过**：用户可以说"不清楚"、"跳过"
- **智能推断**：根据已有信息推断后续答案
- **随时可改**：确认前都可以修改

## 与其他 Skill 的关系

```
/fi-init → 生成 requirement-template.md
  ↓
/fi-plan → 读取 requirement-template.md，生成架构设计
  ↓
... 后续流程
```

## 错误处理

| 情况 | 处理方式 |
|------|----------|
| 用户输入模糊 | 提供选项让用户选择 |
| 用户中途退出 | 保存已收集信息，下次可恢复 |
| 需求过于复杂 | 建议拆分为多个子项目 |
