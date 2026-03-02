---
name: fi-implement
description: 根据测试用例生成实现代码
trigger: /fi-implement
dependencies:
  - superpowers:test-driven-development
  - ui-ux-pro-max
references:
  - ../shared-references/constitution.md
  - ../shared-references/directory-structure.md
  - ../shared-references/git-commit-standards.md
---

# 代码实现 Skill

根据测试用例生成实现代码。

## 前置条件

- 测试用例已生成并确认
- Contracts 类型定义完整
- `docs/architecture.md` 存在且包含模块划分
- 测试处于失败状态（TDD 红灯）或已有部分通过

## 前置条件验证

在执行前必须依次验证：

1. 检查 `server/tests/`（及如有）`client/tests/` 下是否存在测试文件（`*.test.ts` 或 `*.spec.ts`）。
2. 运行 `npx vitest run` 确认测试可执行；**执行范围**：若存在 `server/` 或 `client/` 且其下有 `package.json` 或 `vitest.config.*`，则在各自目录下执行，否则在根目录执行。若 Vitest 未配置则跳过执行检查。
3. 若不存在任何测试文件，停止执行并提示用户先完成 `/fi-test` 并确认测试用例。

## 执行流程

### Step 1: 确定实现范围

**实现范围 = 架构定义的全部模块 + 需求定义的全部页面**，而不仅限于已有测试的模块。

1. **必须**读取 `docs/architecture.md`，提取全部后端模块列表
2. **必须**读取 `docs/requirements.md`，提取全部前端页面清单
3. 读取所有测试文件，识别已有测试覆盖的功能
4. 生成实现清单：架构中的每个模块、需求中的每个页面，均需实现

**禁止**：仅实现有测试的 1-2 个模块后停止；必须实现架构与需求定义的全部功能。

### Step 2: 分析测试用例并确定实现顺序

1. 读取所有测试文件
2. 识别需要实现的功能
3. 按以下顺序实现

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

### Step 3: 服务端实现

对于**架构中列出的每个后端模块**（无论是否有测试）：
1. 若有对应测试：运行测试，编写实现使测试通过
2. 若无对应测试：根据 contracts 和架构 API 设计，实现完整功能
3. 实现内容：Repository/Service/Controller/Routes，注册到 app
4. 运行测试，确认通过

### Step 4: 前端实现（全栈项目）

若项目包含前端（`client/` 存在），**必须**实现需求中列出的全部页面和功能：

1. **先调用 `@ui-ux-pro-max`** 获取前端开发最佳实践指导
2. 对于**需求中的每个页面**（首页、登录/注册、创作工作台、素材预览、我的页面等）：实现完整页面与路由
3. 实现 API 封装（`client/src/api/`）、Store（`client/src/stores/`）、Composables
4. 若有对应测试：运行测试，确认通过

**禁止**：仅实现一个简陋首页后停止；必须实现全部页面与核心交互。
**前端实现要点（遵循 ui-ux-pro-max 规范）：**
- API 请求使用 `fetch` 或 `axios`，类型来自 `client/src/contracts/`
- Store 使用 Pinia，遵循 Composition API 风格
- 组件使用 `<script setup lang=”ts”>` 语法
- 组件设计遵循单一职责、合理的 props 定义、清晰的事件命名
- 状态管理遵循最小化原则，避免冗余状态
- 样式使用 Tailwind CSS 或 Scoped CSS，保持一致性
- 可访问性：语义化标签、键盘导航、ARIA 属性

### Step 5: 外部服务集成（如适用）

若项目涉及外部服务（AI 服务、第三方 API 等）：

1. **配置环境变量**
   - 在 `server/.env` 中添加 API Key 配置
   - 使用 `zod` 验证环境变量完整性

2. **实现服务客户端**
   - 在 `server/src/services/` 下为外部服务创建客户端
   - 如 `ai-service.ts`、`payment-service.ts`
   - 实现错误处理和重试逻辑

3. **替换 Mock 为真实实现**
   - 根据环境变量切换 Mock/真实服务
   - 保持接口一致性

4. **编写集成测试**
   - 在 `server/tests/integration/` 下为外部服务编写集成测试
   - 使用真实 API 进行验证（可选，需配置 API Key）

### Step 6: 持续验证

每实现一个模块后运行测试：

```bash
# 服务端
cd server && npx vitest run

# 前端（如有）
cd client && npx vitest run
```

### Step 7: 完成前终验

全部实现完成后，**必须自动执行**以下三项，**全部通过**才可视为实现完成：

1. `npx vitest run` — 所有测试通过
2. `npx tsc --noEmit` — 类型检查通过
3. `npx vitest run --coverage` — 若项目已配置覆盖率则运行，覆盖率达标（参见工程宪法）

执行范围：若存在 `server/` 或 `client/` 且其下有 `package.json` 或 `vitest.config.*` / `tsconfig.json`，则在各自目录下执行；否则在根目录执行。

- **全部通过**：继续下一步。
- **任一项失败**：继续修复或建议用户运行 `/fi-fix`，**不得**将本次会话标记为实现完成。

### Step 8: Git 提交

终验通过后，自动提交到 git（如果项目是 git 仓库）：

```bash
git add . && \
git commit -m “feat: 完成功能实现

- 服务端模块实现 server/src/modules/
- 前端实现 client/src/（如适用）
- 外部服务集成（如适用）
- 所有测试通过

ForgeAI 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')”
```

完成后提示：
```
✅ 功能实现完成
✅ 所有测试通过
✅ 已提交到 git
下一步：/fi-fix 处理遗留问题 或 /fi-review 代码审查
```

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

server/src/services/           # 外部服务客户端（如适用）
├── ai-service.ts
├── payment-service.ts
└── index.ts

server/src/config/             # 环境变量配置（如适用）
└── env.ts
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

（终验已在 Step 6 完成前终验中执行。）

（终验已在 Step 5 完成前终验中执行。）
