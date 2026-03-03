---
name: fi-implement
description: 根据测试用例生成实现代码（状态驱动流水线模式）
trigger: /fi-implement
dependencies:
  - superpowers:test-driven-development
  - ui-ux-pro-max
references:
  - ../shared-references/constitution.md
  - ../shared-references/directory-structure.md
  - ../shared-references/git-commit-standards.md
---

# 代码实现 Skill（流水线模式）

根据测试用例生成实现代码。采用**状态驱动的流水线模式**：通过 `docs/.implement-queue.md` 跟踪实现进度，支持子 agent 并行执行和断点续跑。

## 核心机制

- **实现队列**：`docs/.implement-queue.md` 是唯一状态存储，记录每个任务的 pending/completed/failed 状态
- **幂等执行**：fi-implement 可安全多次运行，自动跳过已完成任务，只处理 pending 项
- **子 agent 分派**：独立模块通过子 agent 并行实现（跨平台兼容：Cursor Task / Claude Code agents / Codex multi-agent / 顺序降级）
- **增量持久化**：每完成一个任务立即更新队列状态，中断不丢失进度

## 前置条件

- 测试用例已生成并确认
- Contracts 类型定义完整
- `docs/architecture.md` 存在且包含模块划分
- 测试处于失败状态（TDD 红灯）或已有部分通过

## 前置条件验证

在执行前必须依次验证：

1. 检查 `server/tests/`（及如有）`client/tests/` 下是否存在测试文件（`*.test.ts` 或 `*.spec.ts`）。
2. 运行 `npx vitest run` 确认测试可执行；**执行范围**：若存在 `server/` 或 `client/` 且其下有 `package.json` 或 `vitest.config.*`，则在各自目录下执行，否则在根目录执行。若 Vitest 未配置则跳过执行检查。
3. 若不存在任何测试文件，停止执行并提示用户先完成 `/fi-test` 并确认测试用例。

## 执行流程

### Step 1: 确定实现范围并生成队列

**若 `docs/.implement-queue.md` 已存在**：读取队列，跳到 Step 3（断点续跑）。

**若不存在**：生成实现队列。

1. **必须**读取 `docs/architecture.md`，提取全部后端模块列表
2. **必须**读取 `docs/requirements.md`，提取全部前端页面清单和 AI 服务需求
3. 读取所有测试文件，识别已有测试覆盖的功能
4. 在 `docs/.implement-queue.md` 中写入结构化任务清单：

```markdown
# 实现队列

> 由 fi-implement 自动生成，用于跟踪实现进度。支持断点续跑：重新运行 fi-implement 时自动跳过已完成任务。

## 后端模块

| 任务ID | 模块 | 状态 | 测试文件 | 备注 |
|--------|------|------|---------|------|
| srv-auth | auth | pending | server/tests/**/auth* | |
| srv-user | user | pending | server/tests/**/user* | |
| ... | ... | pending | ... | |

## 前端任务

| 任务ID | 任务 | 状态 | 备注 |
|--------|------|------|------|
| fe-infra | API封装 + Stores + 布局组件 | pending | 必须最先执行 |
| fe-home | 首页 | pending | |
| fe-workspace | 创作工作台 | pending | |
| ... | ... | pending | |

## 适配器（若 requirements 列有 AI 服务）

| 任务ID | 适配器 | 状态 | 技能参考 | 备注 |
|--------|--------|------|---------|------|
| adp-llm | LLM | pending | llm-integration | |
| adp-image | Image | pending | dashscope-media | |
| adp-tts | TTS | pending | dashscope-media | |

## 中间件

| 任务ID | 中间件 | 状态 | 备注 |
|--------|--------|------|------|
| mw-error | error handler | pending | |
| mw-quota | quota | pending | |
| mw-validate | validate | pending | |

## 进度统计

- 总任务数：XX
- 已完成：0
- 待执行：XX
- 失败：0
```

**禁止**：仅列出有测试的 1-2 个模块；队列必须覆盖架构与需求定义的全部功能。

### Step 2: 确定执行顺序

按以下依赖关系确定任务执行顺序：

**第一批（基础层，顺序执行）**：
1. `srv-auth`（认证模块，其他模块依赖）
2. `srv-user`（用户模块）

**第二批（业务模块，可并行）**：
3. 其余后端模块（如 topic、script、storyboard、asset、video、project、task 等）

**第三批（中间件，可并行）**：
4. 中间件（error handler、quota、validate）

**第四批（适配器，可并行）**：
5. 外部服务适配器（LLM、Image、TTS 等）

**第五批（前端基础设施，顺序执行）**：
6. `fe-infra`（API 封装 + Stores + 布局组件）

**第六批（前端页面，可并行）**：
7. 各前端页面

### Step 3: 状态驱动执行（核心循环）

```
3.1 读取 docs/.implement-queue.md
3.2 统计各状态任务数量
3.3 若无 pending 任务 → 跳到 Step 5（终验）
3.4 按 Step 2 的依赖顺序，选择下一批可执行任务（同批内无依赖关系）
3.5 分派执行（见下方「子 agent 分派机制」）
3.6 每个任务完成后，立即将 docs/.implement-queue.md 中该任务状态改为 completed
3.7 若任务失败，将状态改为 failed，在备注列记录错误摘要
3.8 更新进度统计
3.9 回到 3.2 继续下一批
3.10 若上下文接近限制或已处理多个任务后需要退出，
    保存当前队列状态，输出：
    "⏸ 实现进度：X/Y 完成，Z 失败。请重新运行 /fi-implement 继续。"
```

#### 子 agent 分派机制（跨平台兼容）

对于每批中的**独立任务**（无互相依赖），优先使用子 agent 并行执行：

**分派策略**：
- 同批内最多 3 个子 agent 并行（留资源给主 agent 协调）
- 每个子 agent 只负责**一个**任务，拥有独立上下文
- 子 agent 定义文件位于 `.claude/agents/`（Claude Code 原生支持；其他平台由主 agent 读取后作为提示使用）

**跨平台兼容指令**：
- 若平台提供子 agent 能力（Cursor 的 Task 工具、Claude Code 的 agents、Codex 的 multi-agent），则启动独立子 agent 执行
- 若平台不支持子 agent，则在当前上下文中顺序执行各任务
- **无论哪种模式，每个任务完成后都必须立即更新队列文件**

**后端模块子 agent 提示模板**（参照 `.claude/agents/module-implementer.md`）：

```
你的任务是实现 {MODULE_NAME} 后端模块。

必读文件：
- docs/architecture.md（找到 {MODULE_NAME} 模块的设计）
- server/src/contracts/{MODULE_NAME}.types.ts
- server/src/contracts/{MODULE_NAME}.interfaces.ts
- server/src/contracts/{MODULE_NAME}.schemas.ts
- server/tests/ 下与 {MODULE_NAME} 相关的测试文件
- prisma/schema.prisma

实现目标：
- server/src/modules/{MODULE_NAME}/ 下的全部文件（repository/service/controller/routes/index）
- 注册路由到 server/src/app.ts

完成标准：cd server && npx vitest run 通过（至少不引入新的失败）

禁止：使用 any 类型、import mocks/、生成骨架占位代码、函数超过 40 行
```

**适配器子 agent 提示模板**（参照 `.claude/agents/adapter-implementer.md`）：

```
你的任务是实现 {ADAPTER_NAME} 外部服务适配器。

⚠ 最重要：先读取全局技能文件获取 API 实现指导：
- LLM 适配器：读取 llm-integration 技能的 SKILL.md
- Image/TTS 适配器：读取 dashscope-media 技能的 SKILL.md
技能文件路径：~/.cursor/skills/{技能名}/SKILL.md 或 C:\Users\<用户>\.cursor\skills\{技能名}\SKILL.md

必读文件：
- 上述技能文件（包含 API 端点、SDK 用法、请求格式）
- docs/architecture.md（外部服务集成章节）
- server/src/contracts/adapters.interfaces.ts

实现目标：server/src/adapters/{ADAPTER_NAME}.adapter.ts
- 必须调用真实 API（非 mock）
- 环境变量缺失时抛出错误
- 仅 USE_MOCK_AI=true 时降级为 mock

禁止：默认返回 mock、硬编码 API Key、使用 any 类型
```

**前端子 agent 提示模板**（参照 `.claude/agents/frontend-implementer.md`）：

```
你的任务是实现前端任务：{TASK_NAME}

必读文件：
- docs/architecture.md（前端页面内容规格）
- docs/requirements.md（该页面的需求和验收标准）
- client/src/contracts/（前端类型定义）
- client/src/router/index.ts
- client/src/stores/（已有 store）
- client/src/api/（已有 API 封装）

实现要求：
- 页面必须包含真实 UI 元素（表单/列表/卡片/按钮），使用 Tailwind CSS
- 必须调用至少一个 API、使用对应 Store
- 处理加载状态、空状态、错误状态
- 使用 <script setup lang="ts"> 语法

禁止：只有标题和描述文字的页面、使用 any 类型、页面少于 30 行
```

### Step 4: 队列完成确认

当队列中所有任务状态为 completed 或 failed 时：

1. 若有 failed 任务：列出失败任务清单，建议重试或人工介入
2. 若全部 completed：进入 Step 5

### Step 5: 完成前终验

全部实现完成后，**必须自动执行**以下三项，**全部通过**才可视为实现完成：

1. `npx vitest run` — 所有测试通过
2. `npx tsc --noEmit` — 类型检查通过
3. `npx vitest run --coverage` — 若项目已配置覆盖率则运行，覆盖率达标（参见工程宪法）

执行范围：若存在 `server/` 或 `client/` 且其下有 `package.json` 或 `vitest.config.*` / `tsconfig.json`，则在各自目录下执行；否则在根目录执行。

- **全部通过**：将 `docs/.implement-queue.md` 底部进度统计更新为「全部完成」，继续下一步。
- **任一项失败**：继续修复或建议用户运行 `/fi-fix`，**不得**将本次会话标记为实现完成。

### Step 6: Git 提交

终验通过后，自动提交到 git（如果项目是 git 仓库）：

```bash
git add . && \
git commit -m "feat: 完成功能实现

- 服务端模块实现 server/src/modules/
- 前端实现 client/src/（如适用）
- 外部服务集成（若 requirements 列有 AI 服务则必须实现）
- 所有测试通过

ForgeAI 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
```

完成后提示：
```
✅ 功能实现完成
✅ 所有测试通过
✅ 已提交到 git
下一步：/fi-fix 处理遗留问题 或 /fi-review 代码审查
```

## 实现原则

参考 `shared-references/constitution.md`：

1. **类型安全** - 无 any，显式返回类型
2. **函数长度** - 不超过 40 行
3. **单一职责** - 每个类/函数只做一件事
4. **错误处理** - 显式处理所有异常

## 输出

**状态文件：**

```
docs/.implement-queue.md       # 实现队列（状态跟踪）
```

**服务端：**

```
server/src/modules/
└── {module}/
    ├── {module}.repository.ts
    ├── {module}.service.ts
    ├── {module}.controller.ts
    ├── {module}.routes.ts
    └── index.ts

server/src/adapters/           # 外部服务适配器（如 requirements 列有 AI 服务）
├── llm.adapter.ts
├── image.adapter.ts
├── tts.adapter.ts
└── index.ts

server/src/middlewares/        # 中间件（error、quota、validate 等）
├── error.middleware.ts
├── quota.middleware.ts
└── validate.middleware.ts

server/src/config/             # 环境变量配置（如适用）
└── env.ts
```

**前端（全栈项目）：**

```
client/src/
├── api/
│   └── {module}.api.ts      # API 请求封装（含 JWT token 注入）
├── stores/
│   └── {module}.ts          # Pinia Store
├── composables/
│   └── use{Module}.ts       # Composable
├── components/
│   ├── AppLayout.vue        # 布局组件
│   └── {Module}/            # 业务组件
│       └── *.vue
└── views/                   # 页面
    └── {Page}.vue
```
