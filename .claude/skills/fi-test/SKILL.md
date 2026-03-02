---
name: fi-test
description: 根据 contracts 生成测试用例，遵循 TDD 原则
trigger: /fi-test
dependencies:
  - superpowers:test-driven-development
references:
  - ../shared-references/testing-standards.md
  - ../shared-references/directory-structure.md
  - ../shared-references/git-commit-standards.md
---

# 测试生成 Skill

根据 contracts 生成测试用例，遵循 TDD 原则。

## 前置条件

- `server/src/contracts/` 存在类型定义
- 架构设计已确认

## 前置条件验证

在执行前必须依次验证：

1. 检查 `server/src/contracts/` 目录是否存在。
2. 确认该目录下至少存在一个 `.ts` 类型定义文件（如 `api.types.ts`、`*.types.ts`、`index.ts` 等）。
3. 若验证不通过，停止执行并提示用户先完成 `/fi-contract` 阶段。

## 执行流程

### Step 1: 调用 TDD Skill

调用 `@superpowers:test-driven-development` 进行测试驱动开发。

### Step 2: 分析架构与 Contracts

1. **必须**读取 `docs/architecture.md`，提取**全部**后端模块列表（如 auth、topic、script、storyboard、asset、video、project、task、user 等）
2. **必须**读取 `docs/requirements.md`，提取**全部**前端页面清单（如首页、登录/注册、创作工作台、素材预览、我的页面等）
3. 读取 `server/src/contracts/` 下的类型定义
4. 生成测试计划，**确保覆盖架构中的每一个模块和需求中的每一个页面**

**覆盖范围强制要求**：
- 后端：架构中列出的每个模块**至少**有一个 API 集成测试或 Service 单元测试
- 前端：需求中列出的每个页面/功能**至少**有一个组件测试或页面测试
- 禁止仅生成 1-2 个模块的测试后停止；必须覆盖全部

### Step 3: 生成服务端测试

根据 `shared-references/testing-standards.md` 生成：
- **Service 测试**：单元测试，mock 依赖
- **API 测试**：集成测试，验证端点

### Step 4: 生成前端测试（全栈项目）

若项目包含前端（`client/`），**必须同时生成**前端测试：

- **Vue 组件测试**：使用 `@vue/test-utils` + `vitest`，在 `client/tests/components/` 下为各页面/组件编写测试；覆盖渲染、用户交互、props/emits、插槽等。
- **Pinia Store 测试**：在 `client/tests/stores/` 下为各 store 编写单元测试；mock API 与依赖，验证 state、getters、actions。
- **Composable 测试**：在 `client/tests/composables/` 下为可复用的 composable 编写测试；隔离逻辑，验证输入输出与边界情况。

模板要点：
- 组件测试：`mount`/`shallowMount`，`getByRole`/`findComponent` 查询，`await wrapper.vm.$nextTick()` 处理异步更新。
- Store 测试：`setActivePinia(createPinia())`，实例化 store，断言 state 与 action 结果。
- 遵循 `shared-references/testing-standards.md` 中的 AAA 与命名规范。

### Step 4.5: 生成外部服务 Mock（如适用）

若项目涉及外部服务（AI 服务、第三方 API 等），**必须生成 Mock 支持**：

**服务端 Mock：**
- 在 `server/src/mocks/` 下为外部服务创建 Mock 实现
- 提供 `mock-ai-service.ts`、`mock-payment-service.ts` 等
- 使用环境变量控制 Mock 开关（如 `USE_MOCK_AI=true`）

**前端 Mock：**
- 在 `client/src/mocks/` 下为 API 调用创建 Mock
- 使用 MSW (Mock Service Worker) 或简单的函数 Mock

**测试配置：**
- 测试环境默认使用 Mock
- 集成测试可选择性启用真实服务

### Step 4.6: 复杂 UI 流程测试（全栈项目）

若项目包含复杂页面流程（如编辑器、设置向导、多步骤表单），**必须生成流程测试**：

- **页面流程测试**：在 `client/tests/pages/` 下为复杂页面生成测试
  - 测试用户交互序列
  - 测试状态流转
  - 测试边界情况（取消、返回、异常）
- **E2E 场景骨架**：在 `client/tests/e2e/` 下生成关键流程的 E2E 测试骨架（使用 Playwright 或 Cypress）

### Step 5: 覆盖边界情况

确保测试覆盖：
- 正常路径
- 边界值
- 错误情况
- 空值处理
- 并发场景

### Step 5.5: 横切关注点测试（如适用）

若项目涉及横切关注点，**必须生成相关测试**：

**权限测试：**
- 在 `server/tests/unit/auth/` 下生成权限测试
  - 测试角色权限边界
  - 测试越权访问场景
  - 测试资源所有权校验

**缓存测试：**
- 若使用缓存，在 `server/tests/unit/cache/` 下生成
  - 测试缓存命中/未命中
  - 测试缓存失效
  - 测试缓存更新

**实时通信测试：**
- 若使用 WebSocket/SSE，在 `server/tests/integration/realtime/` 下生成
  - 测试连接建立/断开
  - 测试消息推送
  - 测试重连机制

### Step 6: 生成后自动校验

生成测试文件后**必须自动执行**（无需用户手动运行）：

- 在包含 vitest 配置的目录执行 `npx vitest run`（若存在 `server/vitest.config.*` 则在 server 下执行，同理 client 或根目录；多子项目则分别执行）。
- **能运行且仅有断言失败**（因尚未实现）：视为符合预期，进入 Step 7 人工确认。
- **运行失败**（语法错误、导入错误、配置错误等）：修正测试代码或配置，再次运行直至测试可执行；仅当”能跑且因未实现而失败”时才进入 Step 7。

### Step 7: 覆盖范围校验（fi-auto 时自动执行）

在人工确认前，**必须**执行覆盖范围校验：

1. 对照 `docs/architecture.md` 的模块划分表，逐项检查是否已有对应测试
2. 对照 `docs/requirements.md` 的前端页面清单，逐项检查是否已有对应测试
3. **若有模块或页面无测试**：补充生成，直至全部覆盖
4. 校验通过后再进入人工确认（或 fi-auto 时跳过确认直接进入 implement）

### Step 8: 人工确认

**当非 fi-auto 调用时**，暂停并提示用户确认：

```
测试用例已生成，请查看 server/tests/（及如有前端则 client/tests/）

确认要点：
1. 架构全部模块是否均有测试？
2. 需求全部页面是否均有测试？
3. 边界情况是否覆盖？
4. 验收标准是否满足？

回复 "确认" 继续进入实现阶段，或提出修改意见。
```

- **若用户提出修改意见**：根据意见修正测试或需求理解，重新生成或更新测试文件，再次展示并重复本确认步骤，直至用户确认或明确结束。
- **当由 fi-auto 调用时**：跳过人工确认，直接进入 Step 9。


### Step 9: Git 提交

用户确认后（或 fi-auto 自动执行），自动提交到 git（如果项目是 git 仓库）：

```bash
git add . && \
git commit -m "test: 添加测试用例

- 生成服务端测试 server/tests/
- 生成前端测试 client/tests/（如适用）
- 生成外部服务 Mock（如适用）
- 生成 E2E 测试骨架（如适用）

ForgeAI 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
```

完成后提示：
```
✅ 测试用例已生成并确认
✅ 已提交到 git
下一步：/fi-implement 实现代码
```

## 测试规范

参考 `shared-references/testing-standards.md`：

1. **AAA 模式** - Arrange, Act, Assert
2. **描述性命名** - should_xxx_when_xxx
3. **单一断言** - 每个测试专注一个断言
4. **Mock 外部依赖** - 隔离测试单元

## 输出

**后端：**

```
server/tests/
├── unit/
│   ├── modules/
│   │   └── {module}/
│   │       └── {module}.service.test.ts
│   └── services/
└── integration/
    └── api/
        └── {module}.api.test.ts

server/src/mocks/              # 外部服务 Mock（如适用）
├── mock-ai-service.ts
└── mock-payment-service.ts
```

**前端（全栈项目）：**

```
client/tests/
├── components/
│   └── {ComponentName}.spec.ts   # 或 .test.ts
├── stores/
│   └── {storeName}.spec.ts
├── composables/
│   └── {composableName}.spec.ts
├── pages/                        # 复杂页面流程测试
│   └── {PageName}.spec.ts
└── e2e/                          # E2E 测试骨架（如适用）
    └── {flow}.spec.ts

client/src/mocks/                 # API Mock（如适用）
├── handlers.ts
└── browser.ts
```

（生成后校验已在 Step 4.5 中执行：确保测试可运行且仅因未实现而失败，再进入人工确认。）
