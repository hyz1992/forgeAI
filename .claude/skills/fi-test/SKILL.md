---
name: fi-test
description: 根据 contracts 生成测试用例，遵循 TDD 原则
trigger: /fi-test
dependencies:
  - superpowers:test-driven-development
references:
  - ../shared-references/testing-standards.md
  - ../shared-references/directory-structure.md
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
3. 若验证不通过，停止执行并提示用户先完成 `/contract` 阶段。

## 执行流程

### Step 1: 调用 TDD Skill

调用 `@superpowers:test-driven-development` 进行测试驱动开发。

### Step 2: 分析 Contracts

1. 读取 `server/src/contracts/` 下的所有类型
2. 识别需要测试的功能点
3. 生成测试计划

### Step 3: 生成单元测试

根据 `shared-references/testing-standards.md` 生成 Service 测试和 API 测试。

### Step 3.5: 生成前端测试（全栈项目）

若项目包含前端（`client/`），需同时生成：

- **Vue 组件测试**：使用 `@vue/test-utils` + `vitest`，在 `client/tests/components/` 下为各页面/组件编写测试；覆盖渲染、用户交互、props/emits、插槽等。
- **Pinia Store 测试**：在 `client/tests/stores/` 下为各 store 编写单元测试；mock  API 与依赖，验证 state、getters、actions。
- **Composable 测试**：在 `client/tests/composables/` 下为可复用的 composable 编写测试；隔离逻辑，验证输入输出与边界情况。

模板要点：
- 组件测试：`mount`/`shallowMount`，`getByRole`/`findComponent` 查询，`await wrapper.vm.$nextTick()` 处理异步更新。
- Store 测试：`setActivePinia(createPinia())`，实例化 store，断言 state 与 action 结果。
- 遵循 `shared-references/testing-standards.md` 中的 AAA 与命名规范。

### Step 4: 覆盖边界情况

确保测试覆盖：
- 正常路径
- 边界值
- 错误情况
- 空值处理
- 并发场景

### Step 4.5: 生成后自动校验

生成测试文件后**必须自动执行**（无需用户手动运行）：

- 在包含 vitest 配置的目录执行 `npx vitest run`（若存在 `server/vitest.config.*` 则在 server 下执行，同理 client 或根目录；多子项目则分别执行）。
- **能运行且仅有断言失败**（因尚未实现）：视为符合预期，进入 Step 5 人工确认。
- **运行失败**（语法错误、导入错误、配置错误等）：修正测试代码或配置，再次运行直至测试可执行；仅当“能跑且因未实现而失败”时才进入 Step 5。

### Step 5: 人工确认

```
测试用例已生成，请查看 server/tests/（及如有前端则 client/tests/）

确认要点：
1. 测试场景是否完整？
2. 边界情况是否覆盖？
3. 验收标准是否满足？

回复 "确认" 继续进入实现阶段，或提出修改意见。
```

- **若用户提出修改意见**：根据意见修正测试或需求理解，重新生成或更新测试文件，再次展示并重复本确认步骤，直至用户确认或明确结束。

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
```

**前端（全栈项目）：**

```
client/tests/
├── components/
│   └── {ComponentName}.spec.ts   # 或 .test.ts
├── stores/
│   └── {storeName}.spec.ts
└── composables/
    └── {composableName}.spec.ts
```

（生成后校验已在 Step 4.5 中执行：确保测试可运行且仅因未实现而失败，再进入人工确认。）
