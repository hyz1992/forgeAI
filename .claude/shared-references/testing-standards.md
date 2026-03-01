# 测试规范

> 本文档定义了项目的测试策略和规范。

---

## 1. 测试金字塔

```
         /\
        /  \    E2E 测试（少量）
       /----\
      /      \  集成测试（适量）
     /--------\
    /          \ 单元测试（大量）
   /------------\
```

- **单元测试**：70%+ 覆盖所有业务逻辑
- **集成测试**：20% 覆盖 API 和数据库交互
- **E2E 测试**：10% 覆盖关键用户流程

---

## 2. 单元测试规范

### 2.1 测试文件组织

```
src/
├── modules/
│   └── user/
│       ├── user.service.ts
│       └── user.service.test.ts    # 测试文件与源文件同目录
```

### 2.2 测试命名

```typescript
// ✅ 使用 describe/it 结构
describe('UserService', () => {
  describe('findById', () => {
    it('should return user when exists', () => {
      // ...
    });

    it('should return null when not found', () => {
      // ...
    });
  });
});
```

### 2.3 AAA 模式

```typescript
it('should calculate total price correctly', () => {
  // Arrange - 准备
  const items = [
    { price: 100, quantity: 2 },
    { price: 50, quantity: 1 },
  ];
  const service = new OrderService();

  // Act - 执行
  const total = service.calculateTotal(items);

  // Assert - 断言
  expect(total).toBe(250);
});
```

### 2.4 边界测试

```typescript
describe('validateAge', () => {
  it('should accept valid age', () => {
    expect(validateAge(25)).toBe(true);
  });

  it('should reject negative age', () => {
    expect(validateAge(-1)).toBe(false);
  });

  it('should reject age over 150', () => {
    expect(validateAge(151)).toBe(false);
  });

  it('should accept boundary values', () => {
    expect(validateAge(0)).toBe(true);
    expect(validateAge(150)).toBe(true);
  });
});
```

---

## 3. Mock 规范

### 3.1 接口 Mock

```typescript
import { vi } from 'vitest';

// 定义接口
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
}

// 创建 Mock
function createMockRepository(): vi.Mocked<UserRepository> {
  return {
    findById: vi.fn(),
    save: vi.fn(),
  };
}

// 使用 Mock
it('should call repository with correct id', async () => {
  const mockRepo = createMockRepository();
  mockRepo.findById.mockResolvedValue({ id: '1', name: 'Test' });

  const service = new UserService(mockRepo);
  await service.getUser('1');

  expect(mockRepo.findById).toHaveBeenCalledWith('1');
});
```

### 3.2 外部服务 Mock

```typescript
import { vi } from 'vitest';

// Mock LLM 服务
function createMockLLMService(): LLMService {
  return {
    generate: vi.fn().mockResolvedValue('Generated text'),
    embed: vi.fn().mockResolvedValue([0.1, 0.2, 0.3]),
  };
}
```

---

## 4. 集成测试规范

### 4.1 API 测试

```typescript
import { buildApp } from '@/app';

describe('User API', () => {
  let app: FastifyInstance;

  beforeAll(async () => {
    app = await buildApp();
    await app.ready();
  });

  afterAll(async () => {
    await app.close();
  });

  it('POST /api/users should create user', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/users',
      payload: {
        name: 'Test User',
        email: 'test@example.com',
      },
    });

    expect(response.statusCode).toBe(201);
    expect(response.json()).toMatchObject({
      code: 0,
      data: { name: 'Test User' },
    });
  });
});
```

### 4.2 数据库测试

```typescript
import { PrismaClient } from '@prisma/client';

describe('User Repository', () => {
  let prisma: PrismaClient;

  beforeAll(async () => {
    prisma = new PrismaClient({
      datasources: { db: { url: 'file:./test.db' } },
    });
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  beforeEach(async () => {
    await prisma.user.deleteMany();
  });

  it('should create and find user', async () => {
    const user = await prisma.user.create({
      data: { name: 'Test', email: 'test@test.com' },
    });

    const found = await prisma.user.findUnique({
      where: { id: user.id },
    });

    expect(found).toEqual(user);
  });
});
```

---

## 5. 前端测试规范

### 5.1 组件测试

```typescript
import { mount } from '@vue/test-utils';
import UserCard from './UserCard.vue';

describe('UserCard', () => {
  it('should display user name', () => {
    const wrapper = mount(UserCard, {
      props: {
        user: { id: '1', name: 'Test User', email: 'test@test.com' },
      },
    });

    expect(wrapper.text()).toContain('Test User');
  });

  it('should emit edit event on click', async () => {
    const wrapper = mount(UserCard, {
      props: { user: { id: '1', name: 'Test' } },
    });

    await wrapper.find('[data-testid="edit-btn"]').trigger('click');

    expect(wrapper.emitted('edit')).toBeTruthy();
  });
});
```

### 5.2 Composable 测试

```typescript
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('should increment count', () => {
    const { count, increment } = useCounter();

    expect(count.value).toBe(0);
    increment();
    expect(count.value).toBe(1);
  });
});
```

---

## 6. 覆盖率要求

### 6.1 目标

| 类型 | 目标 |
|------|------|
| 行覆盖率 | ≥ 90% |
| 分支覆盖率 | ≥ 85% |
| 函数覆盖率 | ≥ 95% |

### 6.2 配置

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      thresholds: {
        lines: 90,
        branches: 85,
        functions: 95,
      },
    },
  },
});
```

---

## 7. 测试原则

### 7.1 FIRST 原则

- **F**ast - 测试要快
- **I**ndependent - 测试要独立
- **R**epeatable - 测试可重复
- **S**elf-validating - 测试自验证
- **T**imely - 测试及时编写

### 7.2 禁止事项

```typescript
// ❌ 禁止测试依赖外部状态
it('should work', async () => {
  // 不要依赖真实数据库、网络
  const data = await fetch('https://api.example.com');
});

// ❌ 禁止测试间共享状态
let sharedData;
it('test1', () => { sharedData = create(); });
it('test2', () => { use(sharedData); }); // 顺序依赖

// ❌ 禁止删除失败测试
// 测试失败时应该修复代码，不是删除测试
```

---

## 8. TDD 流程

```
1. 写一个失败的测试
   ↓
2. 运行测试，确认失败
   ↓
3. 写最小代码使测试通过
   ↓
4. 运行测试，确认通过
   ↓
5. 重构代码
   ↓
6. 重复
```

---

## 9. 测试检查清单

- [ ] 测试命名清晰
- [ ] 使用 AAA 模式
- [ ] 覆盖边界情况
- [ ] Mock 外部依赖
- [ ] 测试独立、可重复
- [ ] 无共享状态
- [ ] 覆盖率达标
