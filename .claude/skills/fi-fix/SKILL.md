---
name: fi-fix
description: 自动修复测试失败、类型错误、CI 问题
trigger: /fi-fix
dependencies:
  - superpowers:systematic-debugging
references:
  - ../shared-references/ci-standards.md
  - ../shared-references/coding-standards.md
  - ../shared-references/git-commit-standards.md
---

# 自动修复 Skill

自动修复测试失败、类型错误、CI 问题。

## 前置条件

- 存在失败的测试
- 或存在类型错误
- 或 CI 未通过

## 前置条件验证

在执行前必须至少满足其一：

1. 存在错误标记：`.ai-engineer/errors.json` 中 `has_errors` 为 true（由 PostToolUse Hook 写入）；或
2. 用户明确提供了错误描述（测试失败、类型错误、Lint 错误等）。

若两者皆无，可先运行测试/类型检查/Lint 收集错误信息后再执行本 Skill。

## 执行流程

### Step 1: 调用调试 Skill

调用 `@superpowers:systematic-debugging` 进行系统化调试。

### Step 2: 收集错误信息

**多目录项目**：若存在 `server/` 和 `client/` 子目录，分别在各自目录下执行命令。

```bash
# 服务端
cd server && npx vitest run 2>&1 | tee test-output.log
cd server && npx tsc --noEmit 2>&1 | tee type-output.log
cd server && npx eslint . 2>&1 | tee lint-output.log

# 前端（如有）
cd client && npx vitest run 2>&1 | tee test-output.log
cd client && npx tsc --noEmit 2>&1 | tee type-output.log
cd client && npx eslint . 2>&1 | tee lint-output.log
```

**单目录项目**：在根目录执行上述命令（去掉 `cd server/client` 前缀）。

### Step 3: 分类错误

| 错误类型 | 示例 | 修复策略 |
|----------|------|----------|
| 类型错误 | `Type 'string' is not assignable to type 'number'` | 修正类型定义或转换 |
| 测试失败 | `expected true to be false` | 分析断言，修复实现或测试 |
| Lint 错误 | `'x' is defined but never used` | 移除未使用变量或添加忽略 |
| 运行时错误 | `Cannot read property 'x' of undefined` | 添加空值检查 |

### Step 4: 逐个修复

对于每个错误：
1. **分析根因** - 为什么会出错？
2. **确定修复点** - 需要修改哪个文件？
3. **实施修复** - 编写修复代码
4. **验证修复** - 运行相关测试

### Step 5: 循环验证

```bash
npx vitest run && npx tsc --noEmit && npx eslint .
```

如果仍有错误，重复 Step 2-4。

### Step 6: Git 提交

所有错误修复完成后，自动提交到 git（如果项目是 git 仓库）：

```bash
git add . && \
git commit -m "fix: 自动修复测试和类型错误

- 修复类型错误
- 修复测试失败
- 修复 Lint 问题

ForgeAI 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
```

完成后提示：
```
✅ 所有错误已修复
✅ 已提交到 git
下一步：/fi-review 代码审查
```

## 重试限制

| 限制类型 | 次数 | 超限处理 |
|----------|------|----------|
| 单类错误 | 3 次 | 请求人工介入 |
| 总尝试 | 10 次 | 暂停，生成报告 |

## 禁止行为

1. ❌ 删除失败测试绕过错误
2. ❌ 使用 `any` 绕过类型错误
3. ❌ 使用 `@ts-ignore` 忽略错误
4. ❌ 注释掉代码绕过 lint

## 输出

- 修复后的代码
- 修复记录日志
- 验证通过的测试报告

## 失败处理

如果达到重试限制仍未修复：

1. 生成错误报告：路径为 **`docs/fix-report.md`**（若 `docs/` 不存在则先创建）。报告至少包含：未解决错误列表（含文件与报错摘要）、每类错误的重试次数、建议的下一步（人工修复或再次运行 `/fi-fix`）。
2. 标记需要人工介入的问题。
3. 提供可能的修复建议。
4. 暂停等待人工确认。
