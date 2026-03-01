# 工程宪法（Constitution）

> 本文档定义了所有项目必须遵守的不可违反规则。违反这些规则的代码必须自动修复。

---

## 1. 类型安全

### 规则 1.1：必须使用 TypeScript strict 模式

```json
// tsconfig.json 必须包含
{
  "compilerOptions": {
    "strict": true
  }
}
```

### 规则 1.2：禁止使用 any 类型

❌ 禁止：
```typescript
function process(data: any) { ... }
const result: any = obj.value;
```

✅ 正确：
```typescript
function process(data: unknown) { ... }
const result: string = obj.value as string;
```

### 规则 1.3：所有函数必须显式声明返回类型

❌ 禁止：
```typescript
function add(a: number, b: number) {
  return a + b;
}
```

✅ 正确：
```typescript
function add(a: number, b: number): number {
  return a + b;
}
```

---

## 2. 函数设计

### 规则 2.1：单函数不得超过 40 行

超过 40 行的函数必须拆分为多个子函数。

### 规则 2.2：函数必须保持单一职责

一个函数只做一件事。

---

## 3. 模块设计

### 规则 3.1：所有模块必须可单独测试

每个模块必须能够独立于其他模块进行单元测试。

### 规则 3.2：禁止循环依赖

模块 A 依赖 B，B 不能依赖 A。

检测方法：
```bash
npx madge --circular src/
```

---

## 4. IO 抽象

### 规则 4.1：所有 IO 必须抽象

文件系统、网络请求、数据库操作必须通过接口抽象，便于测试时 mock。

❌ 禁止：
```typescript
async function loadData() {
  return await fs.readFile('data.json', 'utf-8');
}
```

✅ 正确：
```typescript
interface FileReader {
  read(path: string): Promise<string>;
}

async function loadData(reader: FileReader): Promise<string> {
  return await reader.read('data.json');
}
```

---

## 5. 错误处理

### 规则 5.1：禁止空 catch 块

❌ 禁止：
```typescript
try {
  doSomething();
} catch (e) {
  // 静默忽略
}
```

✅ 正确：
```typescript
try {
  doSomething();
} catch (e) {
  logger.error('Failed to do something', { error: e });
  throw new BusinessError('操作失败', { cause: e });
}
```

### 规则 5.2：所有异常必须显式处理

每个可能抛出异常的操作必须有明确的处理策略：
- 记录日志
- 转换为业务错误
- 重新抛出
- 优雅降级

---

## 6. 测试

### 规则 6.1：必须生成单元测试

所有新功能必须附带单元测试。

### 规则 6.2：覆盖率必须 ≥ 90%

```bash
npx vitest run --coverage
```

覆盖率低于 90% 时，CI 必须失败。

### 规则 6.3：禁止删除失败测试绕过错误

测试失败时，必须修复代码或更新测试逻辑，禁止删除测试。

---

## 7. 代码风格

### 规则 7.1：变量命名

- 变量：camelCase
- 常量：UPPER_SNAKE_CASE
- 类/接口/类型：PascalCase

### 规则 7.2：优先使用 const

优先使用 `const`，必要时才用 `let`，禁止 `var`。

---

## 8. 违规处理

当检测到违反以上规则时：

1. **编译时违规**（类型、语法）：由 tsc 和 eslint 检测，阻止提交
2. **运行时违规**（测试失败）：由 vitest 检测，阻止合并
3. **设计违规**（架构、职责）：由 /review Agent 检测，生成修复建议

违反规则必须自动修复，不得绕过。
