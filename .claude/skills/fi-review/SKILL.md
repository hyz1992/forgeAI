---
name: fi-review
description: 对生成的代码进行质量审查
trigger: /fi-review
dependencies:
  - superpowers:requesting-code-review
references:
  - ../shared-references/constitution.md
  - ../shared-references/coding-standards.md
  - ../shared-references/ci-standards.md
  - ../shared-references/git-commit-standards.md
---

# 代码审查 Skill

对生成的代码进行质量审查。

## 前置条件

- 代码已实现
- 测试已通过

## 前置条件验证

在执行前必须依次验证：

1. 运行 `npx vitest run`（及如有多个子项目则在 server/client 下分别运行），确认所有测试通过。
2. 若存在失败测试，停止执行并提示用户先运行 `/fi-fix` 修复后再进行代码审查。

## 执行流程

### Step 1: 校验宪法文档

```bash
python .claude/scripts/validate.py constitution
```

- **通过**：继续 Step 2。
- **失败**：停止执行，提示先修复 `.claude/shared-references/constitution.md` 再重新运行 `/fi-review`。若为框架维护场景（仅修改预框架本身），可选择性跳过本步。

### Step 2: 调用代码审查 Skill

调用 `@superpowers:requesting-code-review` 进行代码审查。

### Step 3: 执行审查

#### 完整性检查（必须）

- [ ] 对照 `docs/architecture.md`：架构中列出的每个后端模块是否均已实现？
- [ ] 对照 `docs/requirements.md`：需求中列出的每个前端页面是否均已实现？
- [ ] 若存在未实现的模块或页面，**必须**在审查报告中标记为严重问题，并建议用户重新运行 `/fi-implement` 补全。

#### 实现深度检查（必须）

**外部服务集成检查**（当 `docs/requirements.md` 列有 AI 服务时）：
- [ ] `server/src/adapters/` 下是否存在真实适配器（非简单 mock 封装）？
- [ ] 适配器文件中是否包含真实 API 调用代码（fetch/SDK 调用）？
- [ ] Service 文件中是否**不** import `server/src/mocks/`？
- [ ] 若发现 service 直接使用 mock，标记为**严重问题**

**前端实现深度检查**：
- [ ] 每个 Vue 页面文件是否超过 20 行（排除纯占位）？
- [ ] `client/src/stores/` 是否存在且包含 store 文件？
- [ ] `client/src/api/` 是否包含业务 API 模块（非仅 index.ts）？
- [ ] 若发现页面只有标题文字，标记为**严重问题**

**Mock 隔离检查**：
- [ ] `server/src/modules/**/*.ts` 中是否存在 `from '../../mocks/'` 或类似的 mock 导入？
- [ ] 若存在，标记为**严重问题**，建议重新运行 fi-implement

#### 架构合规检查

- [ ] 模块是否符合 contracts 定义？
- [ ] 依赖方向是否正确？
- [ ] 是否存在循环依赖？

若已安装 madge，可执行以下命令检查；未安装则跳过（`npx --no-install madge` 若失败即跳过）：

```bash
npx --no-install madge --circular server/src/ 2>/dev/null || true
npx --no-install madge --circular client/src/ 2>/dev/null || true
```

（Windows 下可省略 `2>/dev/null || true`，命令失败即视为跳过。）

#### 代码质量检查

- [ ] 函数是否超过 40 行？
- [ ] 是否有 any 类型？
- [ ] 是否有空 catch 块？
- [ ] 变量命名是否规范？

#### 安全检查

- [ ] 是否有硬编码的密钥？
- [ ] 是否有 SQL 注入风险？
- [ ] 是否有 XSS 风险？
- [ ] 输入是否经过验证？

#### 性能检查

- [ ] 是否有 N+1 查询？
- [ ] 是否有内存泄漏风险？
- [ ] 是否有阻塞操作？

### Step 4: 生成审查报告

输出路径：**`docs/review-report.md`**（若 `docs/` 不存在则先创建）。内容包含：概述、问题列表、质量评分、总评。

### Step 5: 处理审查结果

| 结果类型 | 处理方式 |
|----------|----------|
| 严重问题 | 调用 `/fi-fix` 修复，重新审查 |
| 重要问题 | 调用 `/fi-fix` 修复 |
| 建议改进 | 记录，可选修复 |

### Step 6: Git 提交

审查完成且无严重问题后，自动提交到 git（如果项目是 git 仓库）：

```bash
git add . && \
git commit -m "docs: 添加代码审查报告

- 质量评分：XX/100
- 问题数量：严重 0 / 重要 X / 建议 X
- 测试覆盖率：XX%

ForgeAI 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
```

完成后提示：
```
✅ 代码审查完成
✅ 已提交到 git
下一步：/fi-run 运行时测试
```

## 审查标准

参考 `shared-references/` 下的文档：
- `constitution.md` - 工程宪法（不可违反规则）
- `coding-standards.md` - 编码规范
- `ci-standards.md` - CI 门控标准

### 必须通过（阻止合并）

| 检查项 | 标准 |
|--------|------|
| TypeScript | 0 errors |
| ESLint | 0 warnings/errors |
| 测试 | 全部通过 |
| 覆盖率 | ≥ 90% |
| 无 any 类型 | 0 处 |
| 无空 catch | 0 处 |
| 无硬编码密钥 | 0 处 |

## 输出

- `docs/review-report.md` — 审查报告（与 `docs/fix-report.md` 同目录约定）
- 如有问题，触发 `/fi-fix` 修复

## 通过标准

1. 无严重问题
2. 重要问题 ≤ 3 个
3. 质量评分 ≥ 80/100
4. 测试覆盖率 ≥ 90%
