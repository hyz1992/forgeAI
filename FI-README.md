# ForgeAI - AI-First 工程预框架

> 一个 AI 驱动的软件工程预框架，通过 Skills 实现从需求到代码的全流程自动化。支持 Claude Code、OpenCode、Cursor、Codex、Antigravity 等平台。

## 概述

ForgeAI 是一套工程化的 AI 开发框架，将软件工程最佳实践固化为可执行的 Skills。通过各平台 Agent 调用 Skills，实现：

- **需求收集** → 结构化的需求文档
- **架构设计** → 符合规范的架构方案
- **类型定义** → 类型安全的接口合同
- **测试驱动** → TDD 流程的测试用例
- **代码实现** → 高质量的实现代码
- **自动修复** → 智能错误修复
- **代码审查** → 全面的质量门控

## 快速开始

在 **Claude Code**、**OpenCode**、**Cursor** 或 **Codex** 等支持 Skills 的 Agent 环境中打开本项目，再按下列步骤操作。

### 1. 安装依赖

```bash
# 进入项目目录
cd ForgeAI

# 运行安装脚本（自动安装外部 Skills）
python .claude/scripts/install.py
```

### 2. 提供想法并生成需求

无需手写需求文档。只需向 Agent 说出产品/项目的**粗略想法**（例如「做一个用户管理系统，能注册登录、管理资料」），然后执行：

```bash
/fi-init      # 通过对话整理你的想法，自动生成 requirement-template.md
```

Agent 会通过少量问答补全信息，并生成结构化的 `requirement-template.md`，无需你逐项填写。

### 3. 按顺序执行后续阶段

在 Claude Code、OpenCode 或 Cursor 等支持的 Agent 环境中，从 `/fi-plan` 起按顺序执行（若尚未生成需求则先执行 `/fi-init`）：

```bash
/fi-init      # 需求收集（仅首次或需重新整理需求时）
/fi-plan      # 架构设计 → 需你确认架构文档
/contract     # 类型定义
/fi-test      # 测试生成 → 需你确认测试用例
/implement    # 代码实现
/fi-fix       # 有错误时修复
/fi-review    # 代码审查 → 需你确认审查报告
```

**全新项目**：在 `/fi-plan` 确认后、执行 `/contract` 前，需准备好项目骨架（`server/`、`client/` 下的 package.json、tsconfig、vitest 配置），或先用全栈脚手架生成项目再接入本流程。详见根目录 `AGENTS.md` 中的「项目骨架约定」。

## Skills 命令

### 核心流程 Skills

| 命令 | 说明 | 确认点 |
|------|------|--------|
| `/fi-init` | 需求收集，生成需求文档 | 否 |
| `/fi-plan` | 架构设计，生成架构文档 | **是** |
| `/contract` | 类型定义，生成 TypeScript 接口 | 否 |
| `/fi-test` | 测试生成，TDD 测试用例 | **是** |
| `/implement` | 代码实现，业务逻辑代码 | 否 |
| `/fi-fix` | 自动修复，错误和问题修复 | 否 |
| `/fi-review` | 代码审查，质量门控检查 | **是** |

「确认点」表示该阶段会生成文档并暂停，等你确认后再继续下一阶段；你可提出修改意见，Agent 会更新后再次请你确认。

### 扩展 Skills

| 命令 | 说明 |
|------|------|
| `/content` | 内容创作（文章、脚本） |
| `/video` | 视频生成（Remotion） |

## 多平台支持

运行 `python .claude/scripts/install.py` 后，除安装外部依赖与 Git Hooks 外，还会创建多平台 Skills 发现路径，便于在 Cursor、Codex 等环境中使用同一套 Skills：

| 平台 | Skills 路径 | 说明 |
|------|-------------|------|
| Claude Code / OpenCode / Antigravity | `.claude/skills/` | 原生支持 |
| Cursor | `.cursor/skills/` | 安装脚本创建链接指向 `.claude/skills/` |
| Codex CLI | `.agents/skills/` | 安装脚本创建链接指向 `.claude/skills/` |

根目录的 `AGENTS.md` 为 Codex、Antigravity 等提供项目上下文与流程说明；在任意平台执行前都可参考。

## 项目结构

```
ForgeAI/
├── .claude/
│   ├── skills/                    # Skills 定义
│   │   ├── fi-init/SKILL.md       # 需求收集
│   │   ├── fi-plan/SKILL.md       # 架构设计
│   │   ├── fi-test/SKILL.md       # 测试生成
│   │   ├── fi-fix/SKILL.md        # 自动修复
│   │   ├── fi-review/SKILL.md     # 代码审查
│   │   ├── contract/SKILL.md      # 类型定义
│   │   ├── implement/SKILL.md     # 代码实现
│   │   ├── content/SKILL.md       # 内容创作
│   │   └── video/SKILL.md         # 视频生成
│   │
│   ├── shared-references/         # 共享参考文档
│   │   ├── constitution.md        # 工程宪法
│   │   ├── requirement-template-structure.md  # 需求文档结构（供 fi-init 生成用）
│   │   ├── tech-stack.md          # 技术栈规范
│   │   ├── directory-structure.md # 目录结构规范
│   │   ├── coding-standards.md    # 编码规范
│   │   ├── testing-standards.md   # 测试规范
│   │   └── ci-standards.md        # CI 规范
│   │
│   ├── scripts/                   # 脚本
│   │   ├── install.py             # 安装脚本
│   │   ├── validate.py            # 校验脚本
│   │   ├── skills.json            # Skills 配置
│   │   └── plugins.json           # Plugins 配置
│   │
│   └── hooks/                     # Git Hooks
│       ├── pre-commit.py          # 提交前检查
│       └── post-tool-use.py       # 工具后处理
│
├── AGENTS.md                      # Agent 指引（多平台）
└── .gitignore
```

根目录的 `requirement-template.md` 由 **/fi-init** 在首次（或重新）收集需求时生成，仓库中不预置；生成结构见 `.claude/shared-references/requirement-template-structure.md`。

运行 `install.py` 后会在项目根目录创建 `.cursor/skills`、`.agents/skills` 的符号链接（或 Windows junction），指向 `.claude/skills`，便于 Cursor、Codex 发现 Skills。

## 开发流程

```
┌─────────────────────────────────────────────────────────────┐
│                      ForgeAI 开发流程                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   /fi-init ──→ /fi-plan ──→ /contract ──→ /fi-test         │
│      │            │                          │               │
│   需求收集     架构设计                    测试生成          │
│      │            │                          │               │
│      ↓        【确认点】                     ↓               │
│      │            │                          │               │
│      └────────────┴──────────────────────────┘               │
│                         │                                    │
│                         ↓                                    │
│                    /implement                                │
│                         │                                    │
│                    代码实现                                  │
│                         │                                    │
│                         ↓                                    │
│   /fi-fix ←───────── 有错误？                               │
│      │                    │                                  │
│   错误修复                 │                                  │
│      │                    ↓                                  │
│      └─────────────→ /fi-review                             │
│                         │                                    │
│                    代码审查                                  │
│                         │                                    │
│                     【确认点】                               │
│                         │                                    │
│                         ↓                                    │
│                      完成 ✅                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 工程宪法

所有生成的代码必须遵守以下规则：

### 类型安全

- ✅ 使用 TypeScript strict 模式
- ❌ 禁止使用 `any` 类型
- ✅ 所有函数显式声明返回类型

### 函数设计

- ✅ 单函数不超过 40 行
- ✅ 保持单一职责

### 测试要求

- ✅ 测试覆盖率 ≥ 90%
- ✅ 遵循 TDD 流程
- ❌ 禁止删除失败测试

### 错误处理

- ❌ 禁止空 catch 块
- ✅ 所有异常显式处理

## 技术栈

### 后端

| 组件 | 选型 |
|------|------|
| 运行时 | Node.js 20+ |
| 框架 | Fastify |
| 语言 | TypeScript (strict) |
| 数据库 | SQLite + Prisma |
| 验证 | Zod |

### 前端

| 组件 | 选型 |
|------|------|
| 框架 | Vue 3 |
| 构建工具 | Vite |
| 状态管理 | Pinia |
| 样式 | Tailwind CSS |

### AI 服务

| 服务 | 提供商 |
|------|--------|
| LLM | 智谱 GLM |
| 生图 | 阿里 DashScope |
| 语音合成 | 阿里 DashScope |
| 视频生成 | Remotion |

## 外部依赖

ForgeAI 依赖以下外部 Skills（通过 `install.py` 自动安装）：

| 包名 | 用途 |
|------|------|
| superpowers | 核心 AI 开发能力 |
| humanizer-zh | 中文内容去 AI 味（可选） |
| baoyu-skills | 内容生成工具包（可选） |

## 配置

### 环境变量

```bash
# server/.env
DATABASE_URL="file:./dev.db"
ZHIPU_API_KEY="your_zhipu_api_key"
DASHSCOPE_API_KEY="your_dashscope_api_key"

# client/.env
VITE_API_BASE_URL="http://localhost:3000"
```

### Git Hooks 与写入后校验

- **pre-commit**（通用）：安装脚本会配置 Git 的 `pre-commit` hook，在**任意平台**提交前自动运行类型检查、Lint、测试。
- **PostToolUse**（仅 Claude Code/Claude 编辑器）：在 `.claude/settings.local.json` 中配置，Agent 用 Write/Edit 写入文件后**自动**运行类型检查、Lint、相关测试，并写 `.ai-engineer/errors.json` 供 `/fi-fix` 参考。  
  **在 OpenCode、Cursor、Codex、Antigravity 中**没有等效的 PostToolUse 机制，可任选其一：
  - **手动校验**：Agent 修改某文件后，在项目根目录执行  
    `python .claude/hooks/post-tool-use.py Edit <该文件路径>`（新建用 `Write`）。
  - **依赖 pre-commit**：不在写入后即时校验，仅在 `git commit` 时由 pre-commit 统一检查。
  - 若所用编辑器支持「保存时运行命令」，可配置保存时执行上述 `post-tool-use.py` 命令。

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 常见问题

- **全新项目没有 server/、client/ 怎么办？** 在 `/fi-plan` 确认架构后，用你惯用的全栈脚手架（如 Vue + Fastify 模板）生成 `server/`、`client/` 及 package.json、tsconfig、vitest 配置，再将本仓库的 `.claude` 等复制进去，或先 clone 本仓库再在空目录里按流程执行，由 contract 等 Skill 按需创建子目录。
- **命令在哪里输入？** 在对应平台的对话/命令栏中输入，例如 Claude Code 的 Slash 命令、Cursor 的 Agent 输入框。

## 许可证

MIT License

---

**ForgeAI** - 让 AI 成为你的工程伙伴
