---
name: fi-plan
description: 根据 docs/requirements.md 生成项目架构设计
trigger: /fi-plan
dependencies:
  - superpowers:writing-plans
references:
  - ../shared-references/constitution.md
  - ../shared-references/tech-stack.md
  - ../shared-references/directory-structure.md
  - ../shared-references/git-commit-standards.md
---

# 架构设计 Skill

根据 `docs/requirements.md` 生成项目架构设计。

## 前置条件

- 存在 `docs/requirements.md` 且内容完整（通常由用户执行 `/fi-init` 后根据粗略想法自动生成）
- 如果不存在或内容不完整，提示用户先运行 `/fi-init`

## 前置条件验证

在执行前必须依次验证：

1. 检查 `docs/requirements.md` 是否存在；不存在则提示用户先运行 `/fi-init`。
2. 运行 `python .claude/scripts/validate.py requirement`。
3. 若校验失败，停止执行并提示用户补充需求或重新运行 `/fi-init`。

## 执行流程

### Step 1: 读取并校验需求

1. 读取 `docs/requirements.md`
2. 运行校验脚本：
   ```bash
   python .claude/scripts/validate.py requirement
   ```
3. 如果校验失败，提示用户补充信息或重新运行 `/fi-init`

### Step 2: 设计架构

调用 `@superpowers:writing-plans` 编写架构计划：

1. 系统架构设计
2. 模块划分
3. 技术选型确认
4. 数据流设计
5. API 设计

**输出内容：**
- 架构概览图
- 模块职责表
- 技术栈确认
- 关键接口定义

### Step 3: 生成架构文档

若 `docs/` 目录不存在则先创建，再创建 `docs/architecture.md`，包含：
- 系统概述
- 系统架构图
- 模块划分
- 技术栈
- 数据流
- API 设计
- **外部服务集成**（如适用）
  - 服务列表（AI 服务、第三方 API 等）
  - 配置方式（环境变量、配置文件）
  - Mock 策略（开发/测试环境）
  - 集成测试计划
- **横切关注点**（如适用）
  - 权限控制方案（RBAC/ABAC/简单角色）
  - 审计日志方案
  - 缓存策略
  - 错误处理统一方案
- **复杂交互处理**（如适用）
  - 多步骤表单状态管理
  - 实时通信方案（WebSocket/SSE）
  - 复杂 UI 组件设计
- **基础设施**（如适用）
  - 数据库迁移策略
  - 多环境配置（开发/测试/生产）
  - CI/CD 流程
- 风险与缓解

### Step 3.5: 项目骨架（若不存在）

若 `server/` 或 `client/` 不存在，或存在但缺少 `package.json`、`tsconfig.json` 等基础配置，**必须**生成项目骨架：

- **全栈项目**：创建 `server/`（Fastify + Prisma + Vitest）和 `client/`（Vue 3 + Vite + Pinia + Vitest）
- **后端项目**：创建 `server/` 及基础目录结构
- **前端项目**：创建 `client/` 及基础目录结构

骨架需包含：`package.json`、`tsconfig.json`、入口文件、基础路由/健康检查端点，以便 contract 和 fi-test 阶段可正常运行。

参考 `shared-references/directory-structure.md` 和 `shared-references/tech-stack.md`。

### Step 4: 人工确认

**暂停并提示用户确认：**

```
架构设计已生成，请查看 docs/architecture.md

确认要点：
1. 架构是否符合预期？
2. 模块划分是否合理？
3. 技术选型是否正确？

回复 "确认" 继续，或提出修改意见。
```

- **若用户提出修改意见**：根据意见更新 `docs/architecture.md`，再次展示并重复本确认步骤，直至用户确认或明确结束。

### Step 5: Git 提交

用户确认后，自动提交到 git（如果项目是 git 仓库）：

```bash
git add . && \
git commit -m "docs: 完成架构设计

- 生成 docs/architecture.md
- 系统架构、模块划分、技术栈已确定

ForgeAI 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
```

完成后提示：
```
✅ 架构设计已完成并提交到 git
下一步：/contract 生成类型定义
```

## 参考文档

执行时必须参考 `shared-references/` 下的以下文档：
- `constitution.md` - 工程规则
- `tech-stack.md` - 技术栈规范
- `directory-structure.md` - 目录结构规范

## 输出

- `docs/architecture.md` - 架构设计文档
- 等待用户确认后进入 `/contract` 阶段

## 失败处理

| 失败类型 | 处理方式 |
|----------|----------|
| 需求不完整 | 提示用户补充 |
| 校验失败 | 显示具体错误 |
| 架构冲突 | 提出替代方案 |
