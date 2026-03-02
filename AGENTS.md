# ForgeAI 项目 Agent 指引

本文件供 **所有支持项目级 Agent 指引的平台** 使用（如 Codex、Antigravity、OpenCode 等）。本仓库使用 **ForgeAI** 预框架，通过结构化 Skills 驱动从需求到代码的全流程。Agent 在执行各阶段任务时，请遵循以下约定。

## Skills 位置

- **Claude Code / OpenCode / Antigravity**：使用 `.claude/skills/` 下的 Skills。
- **Cursor**：使用 `.cursor/skills/`（若存在，指向 `.claude/skills/`）。
- **Codex**：使用 `.agents/skills/`（若存在，指向 `.claude/skills/`）。

运行 `python .claude/scripts/install.py` 会自动创建上述多平台发现路径。

## 开发流程顺序

### 逐步执行模式

1. **需求**：用户只需提供产品/项目的粗略想法，执行 **/fi-init** 后通过对话自动生成 `docs/requirements.md`，生成后**自动运行** `validate.py requirement` 做校验。校验通过再进入下一步，避免下游阶段（架构、合同、测试）拿到残缺需求而产生错误输出。
2. **架构**：根据需求生成 `docs/architecture.md`（/fi-plan）。
3. **合同**：根据架构生成 `server/src/contracts/` 下的 TypeScript 类型（/contract）。
4. **测试**：根据 contracts 生成 TDD 测试（/fi-test）。
5. **实现**：根据测试实现业务代码（/implement）。
6. **修复**：修复类型/测试/CI 问题（/fi-fix）。
7. **审查**：代码质量门控（/fi-review）。

### 全自动模式（推荐）

完成 **/fi-init** 需求收集后，执行 **/fi-auto** 可自动完成步骤 2-7：

```
/fi-init   →  需求收集（用户参与）
    ↓
/fi-auto   →  自动执行：架构 → 合同 → 测试 → 实现 → 修复 → 审查
    ↓
  完成 ✅
```

**执行模式**：
- **全自动**：所有阶段自动执行，仅在完成或出错时暂停
- **阶段确认**：每个阶段完成后暂停，允许检查后再继续
- **关键点确认**：仅在架构设计和代码审查阶段暂停确认

**项目骨架约定**：`/implement` 与 `/fi-test` 需要可运行的 TypeScript/Vitest 环境。项目骨架（如 `server/`、`client/` 下的 `package.json`、`tsconfig.json`、`vitest.config.*`）应在 **fi-plan 确认后、contract 之前** 由用户或脚本生成；或在使用本框架前已存在。contract 会按需创建 `server/src/contracts/` 目录，但不会创建整个工程骨架。

## 规范与标准

所有生成的代码必须符合 `.claude/shared-references/` 下的文档：

- `constitution.md` — 工程宪法（类型安全、函数长度、测试覆盖率等）
- `tech-stack.md` — 技术栈（Node.js、Fastify、Vue 3、Prisma 等）
- `directory-structure.md` — 目录结构
- `coding-standards.md` — 编码规范
- `testing-standards.md` — 测试规范
- `ci-standards.md` — CI 门控

执行前请优先阅读与当前阶段相关的规范，确保输出符合项目约定。

## 文件写入后校验（平台差异）

在 **Claude Code** 中，Write/Edit 写入文件后会通过 PostToolUse 自动运行类型检查、Lint、相关测试。在 **OpenCode、Cursor、Codex、Antigravity** 中无此 hook，可手动在项目根执行：

```bash
python .claude/hooks/post-tool-use.py Edit <文件路径>
```

（新建文件用 `Write` 替代 `Edit`。）也可仅依赖 Git 的 pre-commit 在提交时统一检查。
