---
name: fi-contract
description: 根据架构设计生成类型定义和接口合同
trigger: /fi-contract
dependencies:
  - superpowers:writing-plans
references:
  - ../shared-references/constitution.md
  - ../shared-references/tech-stack.md
  - ../shared-references/directory-structure.md
  - ../shared-references/git-commit-standards.md
---

# 类型与接口合同 Skill

根据架构设计生成类型定义和接口合同。

## 前置条件

- `docs/architecture.md` 存在且已确认
- 架构设计完整，包含模块划分

## 前置条件验证

在执行前必须依次验证：

1. 检查 `docs/architecture.md` 是否存在；不存在则提示用户先完成 `/fi-plan` 并确认架构。
2. 确认架构文档包含关键章节：系统概述、模块划分、API 设计（或等价内容）。
3. 若验证不通过，停止执行并提示用户先完成架构设计。

## 执行流程

### Step 1: 读取架构设计

1. 读取 `docs/architecture.md`
2. **必须**提取**全部**模块列表（如 auth、user、topic、script、storyboard、asset、video、project、task 等），禁止遗漏
3. 识别每个模块的数据实体
4. 分析每个模块的 API 接口

**覆盖要求**：架构中列出的每个模块都必须有对应的 `{module}.types.ts` 和 `{module}.schemas.ts`（如适用）。

### Step 2: 生成服务端类型定义

若 `server/src/contracts/` 不存在则先创建所需层级目录，再在该目录下生成：
- `api.types.ts` - 通用 API 类型
- `{module}.types.ts` - 实体类型
- `{module}.interfaces.ts` - 接口定义
- `{module}.schemas.ts` - Zod 验证
- `index.ts` - 统一导出

### Step 2.5: 生成中间件/横切关注点类型（如适用）

**执行条件**：读取 `docs/architecture.md` 的「横切关注点」章节，若包含权限、配额、错误处理、请求验证等，则本步骤为**必须执行**。

在 `server/src/contracts/` 下生成 `middleware.types.ts`（或 `common.types.ts`），包含：
- `QuotaConfig`、`QuotaUsage` — 配额配置与用量
- `ErrorResponse`、`ApiError`、`ValidationError` — 统一错误响应格式
- `AuthContext`、`JwtPayload` — 认证上下文（若涉及权限）
- 其他横切关注点相关的类型定义

这些类型将供 `server/src/middlewares/` 下的中间件实现使用。

### Step 3: 生成适配器接口（如涉及外部服务）

**执行条件**：读取 `docs/requirements.md` 的「AI 服务需求」和「外部服务集成」章节，若列出了任何外部服务，则本步骤为**必须执行**。

1. 在 `server/src/contracts/` 下生成适配器接口文件（如 `adapters.interfaces.ts` 或按服务拆分 `llm.adapter.ts`、`image.adapter.ts`、`tts.adapter.ts`）
2. 为每个外部服务定义接口，示例：
   - `ILLMAdapter`：`generateTopics`、`generateScript`、`reviewScript` 等
   - `IImageAdapter`：`generate(prompt, options)` 等
   - `ITTSAdapter`：`synthesize(text, options)` 等
3. 这些接口将作为 fi-implement 阶段实现适配器的合同，禁止 service 直接依赖 mock

### Step 4: 生成前端类型定义（全栈项目）

若项目包含前端（`client/` 存在），在 `client/src/contracts/` 下生成：
- `api.types.ts` - API 请求/响应类型（与服务端保持一致）
- `{module}.types.ts` - 实体类型
- `index.ts` - 统一导出

**类型共享原则**：前端类型应与服务端保持一致，可从服务端 contracts 复制或使用 monorepo 共享包。

### Step 5: 生成接口定义

定义 Repository 和 Service 接口。

### Step 6: 生成 Zod Schema

用于请求验证的 Zod Schema。

### Step 7: 生成后校验

生成 contracts 后**必须自动执行**（无需用户手动运行）：

- 在包含 `tsconfig.json` 的目录执行 `npx tsc --noEmit`（若存在 `server/tsconfig.json` 则在 server 下执行，同理 client 或根目录）。
- **通过**：继续下一步。
- **失败**：根据类型报错修正类型或代码，再次运行上述命令，直至通过后再结束。

### Step 8: Git 提交

校验通过后，自动提交到 git（如果项目是 git 仓库）：

```bash
git add . && \
git commit -m "feat(contracts): 添加类型定义

- 生成服务端类型定义 server/src/contracts/
- 生成前端类型定义 client/src/contracts/（如适用）
- 添加 Zod Schema 验证

ForgeAI 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
```

完成后提示：
```
✅ 类型定义已生成并校验通过
✅ 已提交到 git
下一步：/fi-test 生成测试用例
```

## 类型设计原则

参考 `shared-references/constitution.md`：

1. **禁止 any** - 所有类型必须明确
2. **接口优于类型** - 对象结构用 interface
3. **只读优先** - 不可变数据用 readonly
4. **命名规范** - 接口用 I 前缀，类型无前缀

## 输出

**服务端：**

```
server/src/contracts/
├── api.types.ts
├── {module}.types.ts
├── {module}.interfaces.ts
├── {module}.schemas.ts
├── middleware.types.ts     # 或 common.types.ts（如架构含横切关注点）
├── adapters.interfaces.ts  # 或 llm.adapter.ts、image.adapter.ts 等（如涉及外部服务）
└── index.ts
```

**前端（全栈项目）：**

```
client/src/contracts/
├── api.types.ts
├── {module}.types.ts
└── index.ts
```

（终验已在 Step 7 中执行，此处不再重复。）
