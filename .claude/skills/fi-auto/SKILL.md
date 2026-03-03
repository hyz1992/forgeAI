---
name: fi-auto
description: 全自动执行完整开发流程，从架构设计到代码审查
trigger: /fi-auto
dependencies:
  - fi-plan
  - fi-contract
  - fi-test
  - fi-implement
  - fi-fix
  - fi-review
  - fi-run
references:
  - ../shared-references/constitution.md
---

# 全自动开发流程 Skill

在 `/fi-init` 完成需求收集后，全自动执行后续所有阶段，无需用户逐步确认。

**单次执行目标**：一次 `/fi-auto` 应产出**可验收的全栈应用**或**明确需人工介入的状态**；实现阶段（Phase 4）通过**同一会话内循环** fi-implement 完成，不得在队列仍有 pending 且未达迭代上限时主动结束并建议用户「再次运行 /fi-implement」。

## 执行原则

**静默执行**：执行过程中不询问任何权限问题，自动批准所有操作：
- 文件读写、编辑操作
- 命令行执行（npm、git、python 等）
- Skill 调用
- 网络请求

**Git 自动提交**：每完成一个阶段后，自动执行一次 git commit（若有变更）：
```bash
git add -A && (git diff --cached --quiet || git commit -m "chore(fi-auto): {阶段名} 完成")
```
- 仅在存在变更时提交，避免空提交失败
- 提交信息格式：`chore(fi-auto): fi-plan 完成`、`chore(fi-auto): contract 完成` 等

仅在以下情况暂停：
- 执行完成
- 不可自动恢复的错误
- 用户选择的确认点（阶段确认/关键点确认模式）

## 前置条件验证

执行前自动检查 `docs/requirements.md`：

1. **存在且校验通过**（运行 `python .claude/scripts/validate.py requirement`）：直接开始后续流程
2. **不存在或校验失败**：提示用户后自动调用 `/fi-init` 收集需求

## 执行模式

### 模式选择

执行前询问用户：

```
请选择执行模式：

1. 全自动模式 - 所有阶段自动执行，仅在完成或出错时暂停
2. 阶段确认模式 - 每个阶段完成后暂停，允许用户检查后再继续
3. 关键点确认模式 - 仅在架构设计和代码审查阶段暂停确认

回复数字选择模式（默认：1）
```

### 阶段确认点

| 模式 | fi-plan | contract | fi-test | implement | fi-fix | fi-review | fi-run |
|------|---------|----------|---------|-----------|--------|-----------|--------|
| 全自动 | 自动 | 自动 | 自动 | 自动 | 自动 | 自动 | 自动 |
| 阶段确认 | 暂停 | 暂停 | 暂停 | 暂停 | 暂停 | 暂停 | 暂停 |
| 关键点确认 | 暂停 | 自动 | 自动 | 自动 | 自动 | 暂停 | 自动 |

## 执行流程

### Phase 1: 架构设计

```bash
/fi-plan
```

**阶段开始前必读**：`docs/requirements.md`

- **全自动/阶段确认模式**：自动生成架构，记录到 `docs/.fi-auto-log.md`
- **关键点确认模式**：生成架构后暂停，等待用户确认

**输出**：`docs/architecture.md`  
**完成后**：自动 `git commit -m "chore(fi-auto): fi-plan 完成"`（若有变更）

### Phase 2: 类型定义

```bash
/fi-contract
```

**阶段开始前必读**：`docs/requirements.md`、`docs/architecture.md`

自动执行，生成前后端类型定义。

**输出**：
- `server/src/contracts/`
- `client/src/contracts/`（如适用）

**完成后**：自动 `git commit -m "chore(fi-auto): fi-contract 完成"`（若有变更）

### Phase 3: 测试生成

```bash
/fi-test
```

**阶段开始前必读**：`docs/requirements.md`、`docs/architecture.md`、`server/src/contracts/`（类型定义）

自动执行，生成**覆盖架构全部模块和需求全部页面**的测试用例（含 Mock、E2E 骨架）。

**完整性要求**：fi-test 必须为 `docs/architecture.md` 中列出的每个后端模块、`docs/requirements.md` 中列出的每个前端页面生成至少一个测试，禁止仅生成 1-2 个模块的测试。

**输出**：
- `server/tests/`
- `client/tests/`（如适用）
- `server/src/mocks/`（如适用）

**完成后**：自动 `git commit -m "chore(fi-auto): fi-test 完成"`（若有变更）

### Phase 4: 代码实现（循环执行）

```bash
/fi-implement
```

**阶段开始前必读**：`docs/requirements.md`、`docs/architecture.md`（含前端页面内容规格）、`server/src/contracts/`、`server/tests/`（及 `client/tests/`）

fi-implement 采用**状态驱动的流水线模式**，通过 `docs/.implement-queue.md` 跟踪进度，支持断点续跑。

**循环执行逻辑**（最大迭代次数：5 次，任务多时可酌情提高至 8～10 次）：

```
iteration = 0
loop:
  1. 调用 /fi-implement
  2. 读取 docs/.implement-queue.md
  3. 统计各状态任务数：pending / completed / failed
  4. 若全部 completed → 退出循环，进入 Phase 4.5
  5. 若有 failed 任务且该任务已重试 3 次 → 标记为需人工介入，退出循环
  6. 若有 pending 任务 → iteration += 1
     - 若 iteration ≤ 5 → 重新调用 /fi-implement（断点续跑，自动跳过已完成任务）
     - 若 iteration > 5 → 暂停，输出剩余任务清单，提示用户手动继续
```

**Phase 4 执行约束（强制）**：执行 fi-auto 的 Agent 即本流水线的调度者，在 Phase 4 内**必须**遵守：

1. **每轮 fi-implement 结束后必做**：读取 `docs/.implement-queue.md` 统计 pending；若**全部 completed** 则进入 Phase 4.5；若**仍有 pending 且 iteration ≤ 5**，则**必须立即**在同一会话内开始下一轮 fi-implement，**不得**在此时输出「实现进度 X/Y，请重新运行 /fi-implement 继续」并结束会话。
2. **禁止**：在队列仍有 pending 且 iteration ≤ 5 时，输出阶段总结或「下一步建议」并结束会话；仅当 iteration > 5 或存在需人工介入的 failed 时，才允许输出剩余任务并暂停。

**输出**：
- `docs/.implement-queue.md`（实现队列状态文件）
- `server/src/modules/`
- `client/src/`（如适用）
- `server/src/adapters/`（如适用）

**每次迭代完成后**：自动 `git commit -m "chore(fi-auto): fi-implement 进度 X/Y"`（若有变更）
**全部完成后**：自动 `git commit -m "chore(fi-auto): fi-implement 完成"`（若有变更）

### Phase 4.5: 实现完整性自检（fi-auto 自动执行）

在 fi-implement 全部完成后（队列中无 pending 任务）、进入 fi-fix 之前，自动执行以下检查：

1. **队列检查**：
   - `docs/.implement-queue.md` 中无 pending 或 failed 任务

2. **适配器检查**（若 requirements.md 包含 AI 服务需求）：
   - `server/src/adapters/` 下的文件数量 ≥ 外部服务数量
   - 适配器文件中不包含 `createMock` 字样

3. **前端检查**：
   - `client/src/stores/` 下至少存在 1 个 .ts 文件
   - `client/src/api/` 下的 .ts 文件数量 ≥ 后端模块数量
   - 每个 views/*.vue 文件超过 20 行

4. **Mock 隔离检查**：
   - `server/src/modules/` 下的文件不 import `server/src/mocks/`

若任一检查失败：
- 将对应的失败项在 `docs/.implement-queue.md` 中重置为 pending
- 回到 Phase 4 的循环，重新调用 fi-implement 补全缺失部分（增量执行，不重做已完成项）

### Phase 5: 自动修复

```bash
/fi-fix
```

**阶段开始前必读**：`docs/architecture.md`、错误输出（`npx vitest run`、`npx tsc --noEmit`、`npx eslint` 的结果）

自动修复测试失败、类型错误、Lint 问题。

**重试限制**：单类错误 3 次，总尝试 10 次

**完成后**：自动 `git commit -m "chore(fi-auto): fi-fix 完成"`（若有变更）

### Phase 6: 代码审查

```bash
/fi-review
```

**阶段开始前必读**：`docs/requirements.md`、`docs/architecture.md`、`server/src/modules/`、`client/src/`（实现代码）

- **全自动/阶段确认模式**：自动生成审查报告
- **关键点确认模式**：生成报告后暂停，等待用户确认

**输出**：`docs/review-report.md`  
**完成后**：自动 `git commit -m "chore(fi-auto): fi-review 完成"`（若有变更）

### Phase 7: 运行时测试

```bash
/fi-run
```

**阶段开始前必读**：`docs/architecture.md`、`docs/review-report.md`、`server/`、`client/`（项目结构）

代码审查通过后，执行运行时测试：
- 启动前后端服务
- 运行 E2E 测试
- UI 截图分析（可选）

**输出**：`docs/runtime-test-report.md`  
**完成后**：自动 `git commit -m "chore(fi-auto): fi-run 完成"`（若有变更）

## 进度记录

执行过程中实时更新 `docs/.fi-auto-log.md`：

```markdown
# ForgeAI 自动执行日志

## 执行信息
- 开始时间：YYYY-MM-DD HH:mm:ss
- 执行模式：全自动 / 阶段确认 / 关键点确认
- 项目名称：{项目名}

## 执行进度

| 阶段 | 状态 | 开始时间 | 完成时间 | 备注 |
|------|------|---------|---------|------|
| fi-plan | ✅ 完成 | ... | ... | |
| contract | ✅ 完成 | ... | ... | |
| fi-test | ✅ 完成 | ... | ... | |
| implement | ✅ 完成 | ... | ... | 循环 N 次，队列 X/Y 完成 |
| 4.5 完整性自检 | ⏳ 进行中 | ... | - | 失败项回退到队列重跑 |
| fi-fix | ⏸️ 待执行 | - | - | |
| fi-review | ⏸️ 待执行 | - | - | |
| fi-run | ⏸️ 待执行 | - | - | |

## 问题记录

| 阶段 | 问题 | 处理方式 | 状态 |
|------|------|---------|------|
| fi-fix | 类型错误 3 处 | 自动修复 | ✅ 已解决 |
| fi-fix | 测试失败 2 处 | 自动修复 | ✅ 已解决 |

## Git 提交记录

| 阶段 | Commit 信息 | 时间 |
|------|-------------|------|
| fi-plan | chore(fi-auto): fi-plan 完成 | ... |
| contract | chore(fi-auto): contract 完成 | ... |
| ... | ... | ... |

## 统计

- 总执行时间：XX 分钟
- 自动修复次数：XX 次
- 人工介入次数：XX 次
- Git 提交次数：XX 次
```

## 错误处理

### 可自动恢复的错误

| 错误类型 | 处理方式 |
|---------|---------|
| 单元测试失败 | 调用 /fi-fix 自动修复 |
| 类型错误 | 调用 /fi-fix 自动修复 |
| Lint 错误 | 调用 /fi-fix 自动修复 |
| E2E 测试失败 | 调用 /fi-fix 修复后重新测试（最多 3 次） |
| UI 显示问题 | 调用 /fi-fix 修复后重新验证 |

### 需要人工介入的错误

| 错误类型 | 处理方式 |
|---------|---------|
| fi-fix 重试超限 | 暂停，提示用户手动修复 |
| 运行时测试重试超限 | 暂停，展示失败详情 |
| 需求不明确 | 暂停，提示用户补充需求 |
| 外部服务不可用 | 暂停，提示用户检查配置 |
| 审查发现严重问题 | 暂停，展示问题列表 |

## 完成后输出

```
============================================================
🎉 ForgeAI 自动执行完成！
============================================================

📊 执行统计：
- 总耗时：XX 分钟
- 生成文件：XX 个
- Git 提交：XX 次（每阶段自动提交）
- 测试覆盖率：XX%
- E2E 测试：XX/XX 通过
- 代码审查评分：XX/100

📁 生成的文档：
- docs/requirements.md    （需求文档）
- docs/architecture.md    （架构设计）
- docs/runtime-test-report.md （运行时测试报告）
- docs/review-report.md   （审查报告）

✅ 验证结果：
- 类型检查：通过
- 单元测试：全部通过
- E2E 测试：全部通过
- Lint：无错误

============================================================
下一步建议：
1. 配置外部服务 API Key（如适用）
2. 部署到测试环境
3. 进行用户验收测试
============================================================
```

## 与其他 Skill 的关系

```
/fi-init → 生成 docs/requirements.md（用户参与）
    ↓
/fi-auto → 全自动执行以下流程：
    ├── /fi-plan       → 架构设计
    ├── /fi-contract   → 类型定义
    ├── /fi-test       → 测试生成
    ├── /fi-implement  → 代码实现（流水线模式：队列 + 子agent + 断点续跑）
    │   ├── 循环调用 fi-implement（每次处理队列中的 pending 任务）
    │   ├── 子 agent 并行实现独立模块
    │   └── docs/.implement-queue.md 跟踪进度
    ├── Phase 4.5      → 完整性自检（失败项回退队列重跑）
    ├── /fi-fix        → 自动修复（静态测试）
    ├── /fi-review     → 代码审查
    └── /fi-run        → 运行时测试（E2E、UI验证）
    ↓
  完成 ✅
```

## 使用场景

| 场景 | 推荐模式 |
|------|---------|
| 快速原型开发 | 全自动模式 |
| 正式项目开发 | 关键点确认模式 |
| 学习/演示 | 阶段确认模式 |
| CI/CD 集成 | 全自动模式 |
