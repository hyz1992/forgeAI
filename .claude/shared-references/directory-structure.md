# 目录结构规范

> 本文档定义了项目生成的目录结构规范。

---

## 1. 全栈项目标准结构

```
project-root/
├── server/                          # 后端代码
│   ├── src/
│   │   ├── modules/                 # 业务模块（按领域划分）
│   │   │   ├── user/
│   │   │   │   ├── user.controller.ts
│   │   │   │   ├── user.service.ts
│   │   │   │   └── user.routes.ts
│   │   │   └── auth/
│   │   │       ├── auth.controller.ts
│   │   │       ├── auth.service.ts
│   │   │       └── auth.routes.ts
│   │   │
│   │   ├── contracts/               # 类型定义与接口
│   │   │   ├── user.types.ts
│   │   │   ├── auth.types.ts
│   │   │   └── api.types.ts         # 通用 API 类型
│   │   │
│   │   ├── services/                # 共享业务逻辑
│   │   │   ├── logger.service.ts
│   │   │   └── cache.service.ts
│   │   │
│   │   ├── adapters/                # 外部服务适配器
│   │   │   ├── llm.adapter.ts       # LLM 服务适配
│   │   │   ├── storage.adapter.ts   # 存储服务适配
│   │   │   └── queue.adapter.ts     # 队列服务适配
│   │   │
│   │   ├── middlewares/             # 中间件
│   │   │   ├── auth.middleware.ts
│   │   │   ├── error.middleware.ts
│   │   │   └── validate.middleware.ts
│   │   │
│   │   ├── utils/                   # 工具函数
│   │   │   └── helpers.ts
│   │   │
│   │   ├── config/                  # 配置
│   │   │   ├── database.ts
│   │   │   └── app.ts
│   │   │
│   │   └── index.ts                 # 应用入口
│   │
│   ├── tests/
│   │   ├── unit/                    # 单元测试
│   │   │   ├── modules/
│   │   │   └── services/
│   │   └── integration/             # 集成测试
│   │       └── api/
│   │
│   ├── prisma/
│   │   ├── schema.prisma            # 数据库模型
│   │   └── migrations/              # 迁移文件
│   │
│   ├── .env                         # 环境变量
│   ├── .env.example                 # 环境变量模板
│   ├── package.json
│   └── tsconfig.json
│
├── client/                          # 前端代码
│   ├── src/
│   │   ├── views/                   # 页面组件
│   │   │   ├── Home.vue
│   │   │   └── User/
│   │   │       ├── UserList.vue
│   │   │       └── UserDetail.vue
│   │   │
│   │   ├── components/              # 通用组件
│   │   │   ├── common/
│   │   │   │   ├── Button.vue
│   │   │   │   └── Modal.vue
│   │   │   └── layout/
│   │   │       ├── Header.vue
│   │   │       └── Sidebar.vue
│   │   │
│   │   ├── api/                     # API 请求封装
│   │   │   ├── index.ts             # 请求客户端
│   │   │   ├── user.api.ts
│   │   │   └── auth.api.ts
│   │   │
│   │   ├── stores/                  # Pinia 状态
│   │   │   ├── user.store.ts
│   │   │   └── app.store.ts
│   │   │
│   │   ├── composables/             # 组合式函数
│   │   │   └── useAuth.ts
│   │   │
│   │   ├── router/                  # 路由配置
│   │   │   └── index.ts
│   │   │
│   │   ├── styles/                  # 全局样式
│   │   │   └── main.css
│   │   │
│   │   ├── utils/                   # 工具函数
│   │   │   └── helpers.ts
│   │   │
│   │   ├── App.vue                  # 根组件
│   │   └── main.ts                  # 入口文件
│   │
│   ├── tests/
│   │   └── components/              # 组件测试
│   │
│   ├── .env                         # 前端环境变量
│   ├── index.html
│   ├── package.json
│   └── tsconfig.json
│
├── docs/                            # 项目文档
│   ├── api.md                       # API 文档
│   └── deployment.md                # 部署文档
│
├── .github/
│   └── workflows/
│       └── ci.yml                   # CI 配置
│
├── docker-compose.yml               # 本地开发环境
├── .gitignore
└── README.md
```

---

## 2. 目录职责说明

### 2.1 后端目录

| 目录 | 职责 | 约束 |
|------|------|------|
| `modules/` | 业务模块，按领域划分 | 模块间无循环依赖 |
| `contracts/` | 类型定义与接口 | 纯类型，无运行时代码 |
| `services/` | 共享业务逻辑 | 无状态，可测试 |
| `adapters/` | 外部服务适配 | 实现 interface，便于 mock |
| `middlewares/` | 请求处理中间件 | 单一职责 |
| `utils/` | 工具函数 | 纯函数，无副作用 |
| `config/` | 配置文件 | 环境变量驱动 |

### 2.2 前端目录

| 目录 | 职责 | 约束 |
|------|------|------|
| `views/` | 页面组件 | 路由级别 |
| `components/` | 通用组件 | 可复用，无业务逻辑 |
| `api/` | API 请求封装 | 统一错误处理 |
| `stores/` | Pinia 状态 | 按领域划分 |
| `composables/` | 组合式函数 | 可复用逻辑 |
| `router/` | 路由配置 | 路由守卫 |

---

## 3. 文件命名规范

### 3.1 TypeScript 文件

| 类型 | 命名 | 示例 |
|------|------|------|
| 组件 | PascalCase | `UserList.vue` |
| 服务 | kebab-case.service.ts | `user.service.ts` |
| 控制器 | kebab-case.controller.ts | `user.controller.ts` |
| 类型 | kebab-case.types.ts | `user.types.ts` |
| 测试 | kebab-case.test.ts | `user.service.test.ts` |
| 工具 | kebab-case.ts | `date-helpers.ts` |

### 3.2 Vue 文件

```
ComponentName.vue          # 组件
ComponentName.stories.ts   # Storybook（可选）
ComponentName.test.ts      # 测试
```

---

## 4. 模块结构模板

### 4.1 后端模块模板

```
modules/
└── {module-name}/
    ├── {module-name}.routes.ts      # 路由定义
    ├── {module-name}.controller.ts  # 控制器
    ├── {module-name}.service.ts     # 业务逻辑
    └── index.ts                     # 模块导出
```

### 4.2 前端功能模块模板

```
views/
└── {feature-name}/
    ├── {FeatureName}List.vue        # 列表页
    ├── {FeatureName}Detail.vue      # 详情页
    ├── {FeatureName}Form.vue        # 表单组件
    └── composables/
        └── use{FeatureName}.ts      # 功能逻辑
```

---

## 5. 禁止的目录结构

### 5.1 禁止扁平化

❌ 避免：
```
src/
├── userController.ts
├── userService.ts
├── authController.ts
├── authService.ts
└── ...（几十个文件）
```

✅ 推荐：
```
src/
└── modules/
    ├── user/
    │   ├── user.controller.ts
    │   └── user.service.ts
    └── auth/
        ├── auth.controller.ts
        └── auth.service.ts
```

### 5.2 禁止深层嵌套

❌ 避免（超过 4 层）：
```
src/
└── modules/
    └── user/
        └── management/
            └── profile/
                └── settings/
                    └── user.settings.service.ts
```

✅ 推荐（最多 3-4 层）：
```
src/
└── modules/
    └── user/
        └── settings/
            └── user.settings.service.ts
```

---

## 6. 生成项目时的目录创建顺序

1. 创建根目录结构
2. 创建 server/ 及其子目录
3. 创建 client/ 及其子目录
4. 创建配置文件
5. 创建 CI 配置
6. 创建文档目录
