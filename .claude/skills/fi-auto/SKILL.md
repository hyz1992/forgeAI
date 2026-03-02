---
name: fi-auto
description: 全自动执行完整开发流程，从架构设计到代码审查
trigger: /fi-auto
dependencies:
  - fi-plan
  - contract
  - fi-test
  - implement
  - fi-fix
  - fi-review
  - fi-run
references:
  - ../shared-references/constitution.md
---

# 全自动开发流程 Skill

在 `/fi-init` 完成需求收集后，全自动执行后续所有阶段，无需用户逐步确认。

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

- **全自动/阶段确认模式**：自动生成架构，记录到 `docs/.fi-auto-log.md`
- **关键点确认模式**：生成架构后暂停，等待用户确认

**输出**：`docs/architecture.md`  
**完成后**：自动 `git commit -m "chore(fi-auto): fi-plan 完成"`（若有变更）

### Phase 2: 类型定义

```bash
/contract
```

自动执行，生成前后端类型定义。

**输出**：
- `server/src/contracts/`
- `client/src/contracts/`（如适用）

**完成后**：自动 `git commit -m "chore(fi-auto): contract 完成"`（若有变更）

### Phase 3: 测试生成

```bash
/fi-test
```

自动执行，生成所有测试用例（含 Mock、E2E 骨架）。

**输出**：
- `server/tests/`
- `client/tests/`（如适用）
- `server/src/mocks/`（如适用）

**完成后**：自动 `git commit -m "chore(fi-auto): fi-test 完成"`（若有变更）

### Phase 4: 代码实现

```bash
/implement
```

自动执行 TDD 流程，实现所有功能。

**输出**：
- `server/src/modules/`
- `client/src/`（如适用）

**完成后**：自动 `git commit -m "chore(fi-auto): implement 完成"`（若有变更）

### Phase 5: 自动修复

```bash
/fi-fix
```

自动修复测试失败、类型错误、Lint 问题。

**重试限制**：单类错误 3 次，总尝试 10 次

**完成后**：自动 `git commit -m "chore(fi-auto): fi-fix 完成"`（若有变更）

### Phase 6: 代码审查

```bash
/fi-review
```

- **全自动/阶段确认模式**：自动生成审查报告
- **关键点确认模式**：生成报告后暂停，等待用户确认

**输出**：`docs/review-report.md`  
**完成后**：自动 `git commit -m "chore(fi-auto): fi-review 完成"`（若有变更）

### Phase 7: 运行时测试

```bash
/fi-run
```

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
| implement | ⏳ 进行中 | ... | - | |
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
    ├── /fi-plan   → 架构设计
    ├── /contract  → 类型定义
    ├── /fi-test   → 测试生成
    ├── /implement → 代码实现
    ├── /fi-fix    → 自动修复（静态测试）
    ├── /fi-review → 代码审查
    └── /fi-run    → 运行时测试（E2E、UI验证）
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
