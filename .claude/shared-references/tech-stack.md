# 技术栈规范

> 本文档定义了项目的技术选型约束，所有代码必须遵循此规范。

---

## 1. 后端技术栈

### 1.1 运行时与框架

| 组件 | 选型 | 说明 |
|------|------|------|
| 运行时 | Node.js 20+ | LTS 版本 |
| 框架 | Fastify | 高性能，内置验证 |
| 语言 | TypeScript (strict) | 类型安全 |

### 1.2 数据库

| 组件 | 选型 | 说明 |
|------|------|------|
| 数据库 | SQLite | 开发和小型部署 |
| ORM | Prisma | 类型安全的数据库操作 |
| 迁移 | Prisma Migrate | 版本控制的数据库迁移 |

**保留升级 PostgreSQL 的可能：**

Prisma schema 设计时应考虑 PostgreSQL 兼容性：
- 避免使用 SQLite 特有的函数
- 使用标准 SQL 类型
- 在 `schema.prisma` 中保持数据库无关的建模

```prisma
// 推荐：数据库无关的建模
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
}
```

### 1.3 验证

| 组件 | 选型 | 说明 |
|------|------|------|
| 请求验证 | Zod | 运行时类型验证 |
| API 响应 | 统一格式 | `{ code, data, message }` |

**API 响应格式：**

```typescript
// 成功响应
{
  "code": 0,
  "data": { ... },
  "message": "success"
}

// 错误响应
{
  "code": 1001,
  "data": null,
  "message": "用户名已存在"
}
```

---

## 2. 前端技术栈

### 2.1 框架与构建

| 组件 | 选型 | 说明 |
|------|------|------|
| 框架 | Vue 3 | Composition API + `<script setup>` |
| 构建工具 | Vite | 快速开发和构建 |
| 语言 | TypeScript (strict) | 类型安全 |

### 2.2 状态与请求

| 组件 | 选型 | 说明 |
|------|------|------|
| 状态管理 | Pinia | Vue 3 官方推荐 |
| HTTP 请求 | fetch / $fetch | 原生或 Nuxt useFetch |

### 2.3 样式

| 组件 | 选型 | 说明 |
|------|------|------|
| CSS 框架 | Tailwind CSS | 原子化 CSS |
| 组件库 | 按需选择 | Element Plus / Naive UI / 自定义 |

---

## 3. AI 服务

### 3.1 LLM（大语言模型）

| 配置项 | 值 |
|--------|-----|
| 提供商 | 智谱 GLM |
| SDK | OpenAI SDK（兼容接口） |
| 框架 | LangChain.js / LangGraph.js（优先） |

**使用示例：**

```typescript
// 使用 OpenAI SDK 调用 GLM
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.ZHIPU_API_KEY,
  baseURL: 'https://open.bigmodel.cn/api/paas/v4/',
});

const response = await client.chat.completions.create({
  model: 'glm-4',
  messages: [{ role: 'user', content: 'Hello' }],
});
```

**LangChain.js 优先：**

```typescript
import { ChatOpenAI } from '@langchain/openai';

const model = new ChatOpenAI({
  configuration: {
    baseURL: 'https://open.bigmodel.cn/api/paas/v4/',
  },
});
```

### 3.2 生图模型

| 配置项 | 值 |
|--------|-----|
| 提供商 | 阿里 DashScope |
| 模型 | wan2.6-t2i |

**环境变量：**
```bash
DASHSCOPE_API_KEY=your_api_key
```

### 3.3 语音合成

| 配置项 | 值 |
|--------|-----|
| 提供商 | 阿里 DashScope |
| 模型 | qwen3-tts-flash |

### 3.4 视频生成

| 配置项 | 值 |
|--------|-----|
| 框架 | Remotion |
| 方式 | 代码驱动渲染 |

**Remotion 特点：**
- 使用 React/TypeScript 编写视频
- 精确控制每一帧
- 支持 MP4、WebM 输出
- 可编程动画和时间线

---

## 4. 工程工具

### 4.1 代码质量

| 工具 | 用途 |
|------|------|
| ESLint | 代码规范检查 |
| Prettier | 代码格式化 |
| TypeScript | 类型检查 |

### 4.2 测试

| 工具 | 用途 |
|------|------|
| Vitest | 单元测试、集成测试 |
| Coverage | 覆盖率报告（≥90%） |

### 4.3 CI/CD

| 工具 | 用途 |
|------|------|
| GitHub Actions | 持续集成 |
| Docker | 容器化部署 |

---

## 5. 环境变量管理

### 5.1 后端环境变量

```bash
# server/.env
DATABASE_URL="file:./dev.db"
ZHIPU_API_KEY="your_zhipu_api_key"
DASHSCOPE_API_KEY="your_dashscope_api_key"
```

### 5.2 前端环境变量

```bash
# client/.env
VITE_API_BASE_URL="http://localhost:3000"
```

### 5.3 安全要求

- 环境变量文件（`.env`）必须加入 `.gitignore`
- 禁止在代码中硬编码 API Key
- 提供 `.env.example` 作为模板

---

## 6. 目录结构约定

```
project-root/
├── server/                    # 后端代码
│   ├── src/
│   │   ├── modules/           # 业务模块
│   │   ├── contracts/         # 类型定义与接口
│   │   ├── services/          # 业务逻辑
│   │   ├── adapters/          # 外部服务适配器
│   │   └── index.ts           # 入口文件
│   ├── tests/
│   │   ├── unit/              # 单元测试
│   │   └── integration/       # 集成测试
│   ├── prisma/
│   │   └── schema.prisma      # 数据库模型
│   └── .env                   # 后端环境变量
│
├── client/                    # 前端代码
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── components/        # 通用组件
│   │   ├── api/               # API 请求封装
│   │   ├── stores/            # Pinia 状态
│   │   └── main.ts            # 入口文件
│   ├── tests/
│   └── .env                   # 前端环境变量
│
└── .env.example               # 环境变量模板
```

---

## 7. API 规范

### 7.1 RESTful 路由

```
GET    /api/users           # 获取用户列表
GET    /api/users/:id       # 获取单个用户
POST   /api/users           # 创建用户
PUT    /api/users/:id       # 更新用户
DELETE /api/users/:id       # 删除用户
```

### 7.2 请求验证

使用 Zod 定义请求 schema：

```typescript
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(50),
  password: z.string().min(8),
});

type CreateUserInput = z.infer<typeof CreateUserSchema>;
```

---

## 8. 技术栈变更流程

技术栈变更必须满足以下条件：

1. 有明确的技术或业务原因
2. 经过团队讨论和评估
3. 更新本文档
4. 通知所有相关人员

未经批准，不得擅自引入新的技术组件。
