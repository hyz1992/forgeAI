---
name: implement
description: 根据测试用例生成实现代码
trigger: /implement
dependencies:
  - superpowers:test-driven-development
references:
  - ../shared-references/constitution.md
  - ../shared-references/directory-structure.md
---

# 代码实现 Skill

根据测试用例生成实现代码。

## 前置条件

- 测试用例已生成并确认
- Contracts 类型定义完整
- 测试处于失败状态（TDD 红灯）

## 前置条件验证

在执行前必须依次验证：

1. 检查 `server/tests/`（及如有）`client/tests/` 下是否存在测试文件（`*.test.ts` 或 `*.spec.ts`）。
2. 运行 `npx vitest run` 确认测试可执行；**执行范围**：若存在 `server/` 或 `client/` 且其下有 `package.json` 或 `vitest.config.*`，则在各自目录下执行，否则在根目录执行。若 Vitest 未配置则跳过执行检查。
3. 若不存在任何测试文件，停止执行并提示用户先完成 `/fi-test` 并确认测试用例。

## 执行流程

### Step 1: 分析测试用例

1. 读取所有测试文件
2. 识别需要实现的功能
3. 确定实现顺序

**服务端实现顺序：**
1. 基础工具函数
2. 数据模型
3. Repository 层
4. Service 层
5. Controller 层
6. 路由注册

**前端实现顺序：**
1. API 请求封装（`client/src/api/`）
2. Pinia Store（`client/src/stores/`）
3. Composables（`client/src/composables/`）
4. 组件（`client/src/components/`）
5. 页面（`client/src/pages/` 或 `client/src/views/`）
6. 路由配置（`client/src/router/`）

### Step 2: 服务端实现

对于每个服务端测试文件：
1. 运行测试，查看失败原因
2. 编写最小实现使测试通过
3. 运行测试，确认通过
4. 重构代码（可选）

### Step 3: 前端实现（全栈项目）

若项目包含前端（`client/` 存在且有测试），对于每个前端测试文件：
1. 运行测试，查看失败原因
2. 编写最小实现使测试通过
3. 运行测试，确认通过
4. 重构代码（可选）

**前端实现要点：**
- API 请求使用 `fetch` 或 `axios`，类型来自 `client/src/contracts/`
- Store 使用 Pinia，遵循 Composition API 风格
- 组件使用 `<script setup lang=”ts”>` 语法

### Step 4: 持续验证

每实现一个模块后运行测试：

```bash
# 服务端
cd server && npx vitest run

# 前端（如有）
cd client && npx vitest run
```

### Step 5: 完成前终验

全部实现完成后，**必须自动执行**以下三项，**全部通过**才可视为实现完成：

1. `npx vitest run` — 所有测试通过
2. `npx tsc --noEmit` — 类型检查通过
3. `npx vitest run --coverage` — 若项目已配置覆盖率则运行，覆盖率达标（参见工程宪法）

执行范围：若存在 `server/` 或 `client/` 且其下有 `package.json` 或 `vitest.config.*` / `tsconfig.json`，则在各自目录下执行；否则在根目录执行。

- **全部通过**：提示”实现完成，可进行 /fi-review 或先运行 /fi-fix 处理其他问题”。
- **任一项失败**：继续修复或建议用户运行 `/fi-fix`，**不得**将本次会话标记为实现完成。

## 实现原则

参考 `shared-references/constitution.md`：

1. **类型安全** - 无 any，显式返回类型
2. **函数长度** - 不超过 40 行
3. **单一职责** - 每个类/函数只做一件事
4. **错误处理** - 显式处理所有异常

## 输出

**服务端：**

```
server/src/modules/
└── {module}/
    ├── {module}.repository.ts
    ├── {module}.service.ts
    ├── {module}.controller.ts
    ├── {module}.routes.ts
    └── index.ts
```

**前端（全栈项目）：**

```
client/src/
├── api/
│   └── {module}.ts          # API 请求封装
├── stores/
│   └── {module}.ts          # Pinia Store
├── composables/
│   └── use{Module}.ts       # Composable
├── components/
│   └── {Module}/            # 组件目录
│       └── *.vue
└── pages/                   # 页面（如使用 unplugin-vue-router）
    └── {module}/
        └── index.vue
```

（终验已在 Step 5 完成前终验中执行。）
