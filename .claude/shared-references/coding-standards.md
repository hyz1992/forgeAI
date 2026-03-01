# 编码规范

> 本文档定义了项目的编码风格和最佳实践。

---

## 1. TypeScript 规范

### 1.1 类型定义

**优先使用 interface，复杂类型用 type：**

```typescript
// ✅ 对象结构用 interface
interface User {
  id: string;
  name: string;
  email: string;
}

// ✅ 联合类型、工具类型用 type
type Status = 'pending' | 'active' | 'inactive';
type UserKeys = keyof User;
type PartialUser = Partial<User>;
```

### 1.2 泛型使用

```typescript
// ✅ 泛型命名使用大写单字母或语义化名称
function getFirstItem<T>(items: T[]): T | undefined {
  return items[0];
}

// ✅ 约束泛型
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

### 1.3 枚举使用

```typescript
// ✅ 字符串枚举（推荐）
enum UserRole {
  Admin = 'admin',
  User = 'user',
  Guest = 'guest',
}

// ✅ 常量枚举（性能更好）
const enum HttpStatus {
  OK = 200,
  BadRequest = 400,
  NotFound = 404,
}
```

---

## 2. 函数规范

### 2.1 函数签名

```typescript
// ✅ 显式参数和返回类型
function createUser(name: string, email: string): User {
  return { id: crypto.randomUUID(), name, email };
}

// ✅ 可选参数放最后
function fetchUser(id: string, includeDeleted?: boolean): Promise<User> {
  // ...
}

// ✅ 默认参数
function formatDate(date: Date, format: string = 'YYYY-MM-DD'): string {
  // ...
}
```

### 2.2 箭头函数

```typescript
// ✅ 简单回调用箭头函数
const numbers = [1, 2, 3];
const doubled = numbers.map(n => n * 2);

// ✅ 保持 this 上下文用箭头函数
class Counter {
  private count = 0;

  increment = (): void => {
    this.count++;
  };
}
```

### 2.3 函数长度

- 单函数不超过 **40 行**
- 超过时拆分为子函数
- 每个函数只做一件事

---

## 3. 异步编程

### 3.1 async/await

```typescript
// ✅ 使用 async/await
async function fetchUserData(userId: string): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.status}`);
  }
  return response.json();
}

// ✅ 并行请求
async function fetchAll(): Promise<[User[], Post[]]> {
  const [users, posts] = await Promise.all([
    fetchUsers(),
    fetchPosts(),
  ]);
  return [users, posts];
}
```

### 3.2 错误处理

```typescript
// ✅ 明确的错误处理
async function safeFetchUser(id: string): Promise<Result<User, ApiError>> {
  try {
    const user = await fetchUser(id);
    return { success: true, data: user };
  } catch (error) {
    return {
      success: false,
      error: { code: 'FETCH_ERROR', message: String(error) }
    };
  }
}

// ✅ Result 类型定义
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };
```

---

## 4. 类与对象

### 4.1 类设计

```typescript
// ✅ 使用 class 和访问修饰符
class UserService {
  private readonly repository: UserRepository;

  constructor(repository: UserRepository) {
    this.repository = repository;
  }

  async findById(id: string): Promise<User | null> {
    return this.repository.find(id);
  }
}

// ✅ 使用 readonly 表示不可变
interface Config {
  readonly apiUrl: string;
  readonly timeout: number;
}
```

### 4.2 对象构建

```typescript
// ✅ 工厂函数
function createUser(props: CreateUserProps): User {
  return {
    id: crypto.randomUUID(),
    ...props,
    createdAt: new Date(),
  };
}

// ✅ Builder 模式（复杂对象）
class QueryBuilder {
  private conditions: string[] = [];

  where(condition: string): this {
    this.conditions.push(condition);
    return this;
  }

  build(): string {
    return `SELECT * WHERE ${this.conditions.join(' AND ')}`;
  }
}
```

---

## 5. 注释规范

### 5.1 何时注释

```typescript
// ✅ 注释"为什么"，而不是"是什么"
// 使用二分查找优化，因为用户列表通常已排序
function findUser(users: User[], id: string): User | undefined {
  // ...
}

// ✅ TODO 和 FIXME
// TODO: 添加缓存支持
// FIXME: 处理超大文件的情况
```

### 5.2 JSDoc

```typescript
/**
 * 获取用户信息
 * @param userId - 用户ID
 * @param options - 可选配置
 * @returns 用户信息，如果不存在返回 null
 * @throws {NotFoundError} 用户不存在时抛出
 * @example
 * ```ts
 * const user = await getUser('123');
 * ```
 */
async function getUser(
  userId: string,
  options?: GetUserOptions
): Promise<User | null> {
  // ...
}
```

---

## 6. 导入导出

### 6.1 导入顺序

```typescript
// 1. Node.js 内置模块
import fs from 'fs';
import path from 'path';

// 2. 第三方模块
import { z } from 'zod';
import { FastifyInstance } from 'fastify';

// 3. 项目内部模块（别名）
import { UserService } from '@/services/user.service';
import { User } from '@/contracts/user.types';

// 4. 相对导入
import { helper } from './utils';
```

### 6.2 导出风格

```typescript
// ✅ 命名导出（推荐）
export function createUser() { }
export function deleteUser() { }
export type { User, CreateUserInput };

// ✅ 默认导出（仅模块主入口）
export default class UserService { }

// ✅ 重新导出
export { UserService } from './user.service';
export type { User } from './user.types';
```

---

## 7. 代码组织

### 7.1 文件结构

```typescript
// 1. 导入
import { z } from 'zod';

// 2. 常量
const MAX_RETRIES = 3;

// 3. 类型定义
interface Config { }

// 4. 主类/函数
export class Service { }

// 5. 辅助函数
function helper() { }
```

### 7.2 模块边界

- 每个模块有明确的职责
- 通过 index.ts 控制公开 API
- 内部实现放在模块内部

---

## 8. 禁止事项

### 8.1 类型相关

```typescript
// ❌ 禁止 any
function process(data: any) { }

// ❌ 禁止非空断言（除非确定安全）
const name = user.name!;

// ❌ 禁止 @ts-ignore
// @ts-ignore
someCode();
```

### 8.2 代码风格

```typescript
// ❌ 禁止 var
var x = 1;

// ❌ 禁止空代码块
if (condition) { }

// ❌ 禁止魔法数字
setTimeout(callback, 3000); // 应该用常量
```

---

## 9. 代码审查检查清单

- [ ] 类型安全，无 any
- [ ] 函数有显式返回类型
- [ ] 函数不超过 40 行
- [ ] 错误有明确处理
- [ ] 无魔法数字
- [ ] 注释有意义
- [ ] 导入有组织
