# Git 提交规范

## 自动提交原则

每个阶段完成后，如果项目是 git 仓库，自动提交更改。

## 提交时机

| 阶段 | 提交条件 | 提交信息模板 |
|------|---------|-------------|
| fi-init | `requirement-template.md` 生成后 | `docs: 完成需求收集` |
| fi-plan | `docs/architecture.md` 生成后 | `docs: 完成架构设计` |
| contract | 类型定义文件生成后 | `feat(contracts): 添加类型定义` |
| fi-test | 测试文件生成后 | `test: 添加测试用例` |
| implement | 实现代码完成后 | `feat: 完成功能实现` |
| fi-fix | 修复完成后 | `fix: 自动修复测试和类型错误` |
| fi-review | `docs/review-report.md` 生成后 | `docs: 添加代码审查报告` |
| fi-run | `docs/runtime-test-report.md` 生成后 | `docs: 添加运行时测试报告` |

## 提交流程

```bash
# 1. 检查是否是 git 仓库
git rev-parse --is-inside-work-tree

# 2. 检查是否有更改
git status --porcelain

# 3. 如果有更改，执行提交
git add . && git commit -m "<提交信息>

ForgeAI 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"

# 4. 可选：推送到远程（如果配置了远程仓库）
# git push origin <current-branch>
```

## 提交信息格式

**重要：提交日志必须使用中文**

```
<type>(<scope>): <subject>

<body>

ForgeAI 自动提交 - <timestamp>
```

### Type 类型

- `feat`: 新功能
- `fix`: 修复问题
- `docs`: 文档更改
- `test`: 测试相关
- `refactor`: 重构
- `chore`: 构建/工具变更

### 示例

```
feat(认证): 完成用户认证模块

- 实现登录/注册功能
- 添加 JWT 验证中间件
- 完成权限控制

ForgeAI 自动提交 - 2024-01-15 14:30:00
```

## 注意事项

1. **使用中文**：提交日志的 subject、body 必须使用中文
2. **仅在阶段完成后提交**：不在阶段执行过程中提交
3. **跳过空提交**：如果没有文件更改，跳过提交
4. **不推送**：默认只提交到本地，不自动推送（除非用户配置）
5. **保留用户更改**：如果用户手动修改了文件，一起提交
