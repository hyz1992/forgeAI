# CI 规范

> 本文档定义了项目的持续集成规范。

---

## 1. CI 概述

**CI（持续集成）** 是每次代码提交后自动运行的检查流程，确保代码质量。

### 1.1 CI 的作用

| 检查类型 | 工具 | 目的 |
|----------|------|------|
| 类型检查 | TypeScript | 捕获类型错误 |
| 代码规范 | ESLint | 统一代码风格 |
| 测试 | Vitest | 验证功能正确 |
| 覆盖率 | Coverage | 确保测试充分 |
| 安全审计 | audit-ci | 检查依赖漏洞 |
| 构建 | build | 验证可编译 |

---

## 2. 本地 CI（快速反馈）

### 2.1 推荐命令

```bash
# 类型检查
npx tsc --noEmit

# 代码规范
npx eslint . --max-warnings 0

# 运行测试
npx vitest run

# 测试 + 覆盖率
npx vitest run --coverage

# 依赖安全审计
npx audit-ci --moderate

# 构建
npm run build
```

### 2.2 pre-commit Hook

```bash
#!/bin/bash
# 提交前自动运行

echo "🔍 Running pre-commit checks..."

# 只检查暂存的文件
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|vue)$')

if [ -n "$STAGED_FILES" ]; then
  echo "📝 Type checking..."
  npx tsc --noEmit

  echo "📏 Linting..."
  npx eslint $STAGED_FILES --max-warnings 0

  echo "✅ Pre-commit checks passed"
fi
```

---

## 3. GitHub Actions 配置

### 3.1 标准 CI 工作流

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality-gate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      # 静态检查
      - name: Type Check
        run: npx tsc --noEmit

      - name: Lint
        run: npx eslint . --max-warnings 0

      # 测试与覆盖率
      - name: Run Tests
        run: npx vitest run --coverage

      - name: Coverage Threshold
        run: |
          COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$COVERAGE < 90" | bc -l) )); then
            echo "❌ Coverage $COVERAGE% is below 90%"
            exit 1
          fi
          echo "✅ Coverage: $COVERAGE%"

      # 依赖安全
      - name: Dependency Audit
        run: npx audit-ci --moderate

      # 构建
      - name: Build
        run: npm run build

      # 上传覆盖率报告
      - name: Upload Coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage/lcov.info
```

### 3.2 前后端分离项目

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  server:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: server

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: server/package-lock.json

      - run: npm ci
      - run: npx tsc --noEmit
      - run: npx eslint . --max-warnings 0
      - run: npx vitest run --coverage
      - run: npm run build

  client:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: client

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: client/package-lock.json

      - run: npm ci
      - run: npx tsc --noEmit
      - run: npx eslint . --max-warnings 0
      - run: npx vitest run
      - run: npm run build
```

---

## 4. CI 门控标准

### 4.1 必须通过的检查

| 检查项 | 标准 | 失败后果 |
|--------|------|----------|
| TypeScript | 0 errors | 阻止合并 |
| ESLint | 0 warnings/errors | 阻止合并 |
| Vitest | 所有测试通过 | 阻止合并 |
| 覆盖率 | ≥ 90% | 阻止合并 |
| 安全审计 | 无高危漏洞 | 警告 |

### 4.2 分支保护规则

```yaml
# GitHub Branch Protection
branches:
  - name: main
    protection:
      required_status_checks:
        strict: true
        contexts:
          - quality-gate
      required_pull_request_reviews:
        required_approving_review_count: 1
      enforce_admins: true
```

---

## 5. CI 失败处理

### 5.1 常见失败原因

| 失败类型 | 原因 | 解决方案 |
|----------|------|----------|
| tsc 失败 | 类型错误 | 修复类型定义 |
| eslint 失败 | 代码规范问题 | 自动修复或手动修复 |
| 测试失败 | 功能问题 | 修复代码或更新测试 |
| 覆盖率不足 | 测试不充分 | 添加测试用例 |
| 依赖漏洞 | 安全风险 | 更新依赖版本 |

### 5.2 自动修复流程

```
CI 失败
    ↓
解析错误日志
    ↓
分类错误类型
    ├─ 类型错误 → /fix 修复类型定义
    ├─ Lint 错误 → /fix 自动修复
    ├─ 测试失败 → /fix 分析并修复
    └─ 覆盖率不足 → /test 补充测试
    ↓
提交修复
    ↓
重新触发 CI
    ↓
循环直到通过
```

### 5.3 最大尝试次数

- 单类错误最大修复尝试：**3 次**
- 总体最大尝试：**10 次**
- 超过后暂停，请求人工介入

---

## 6. 缓存优化

### 6.1 依赖缓存

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'  # 自动缓存 node_modules
```

### 6.2 构建缓存

```yaml
- name: Cache Build
  uses: actions/cache@v4
  with:
    path: |
      dist
      .vite
    key: build-${{ hashFiles('src/**') }}
```

---

## 7. 通知配置

### 7.1 失败通知

```yaml
- name: Notify on Failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    channel-id: 'C0123456789'
    slack-message: |
      ❌ CI Failed on ${{ github.repository }}
      Branch: ${{ github.ref }}
      Commit: ${{ github.sha }}
```

---

## 8. CI 检查清单

- [ ] TypeScript 编译通过
- [ ] ESLint 无警告/错误
- [ ] 所有测试通过
- [ ] 覆盖率 ≥ 90%
- [ ] 无高危依赖漏洞
- [ ] 构建成功
- [ ] 分支保护规则已配置
