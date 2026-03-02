---
name: fi-content
description: 用于生成自媒体内容，如文章、脚本等
trigger: /fi-content
dependencies: []  # 可选：humanizer-zh, baoyu-skills 等外部工具
---

# 内容创作 Skill

用于生成自媒体内容，如文章、脚本等。

## 前置条件

- 项目已初始化
- LLM 服务已配置（智谱 GLM）

## 执行流程

### Step 1: 确定内容类型

询问用户需要生成什么类型的内容：

1. **公众号文章** - 长图文内容
2. **视频脚本** - 短视频/长视频脚本
3. **产品文案** - 营销文案
4. **社交媒体** - 微博/小红书等

### Step 2: 收集创作需求

```
请提供以下信息：

1. 主题：[内容主题]
2. 目标受众：[受众描述]
3. 风格：[正式/轻松/专业/幽默]
4. 长度：[字数/时长]
5. 关键词：[SEO 关键词]
6. 参考素材：[可选]
```

### Step 3: 调用 LLM 生成

使用配置的 LLM 服务（智谱 GLM）：

```typescript
// 使用 LangChain.js 调用
import { ChatOpenAI } from '@langchain/openai';
import { PromptTemplate } from '@langchain/core/prompts';

const model = new ChatOpenAI({
  modelName: 'glm-4',
  configuration: {
    baseURL: 'https://open.bigmodel.cn/api/paas/v4/',
    apiKey: process.env.ZHIPU_API_KEY,
  },
});

const prompt = PromptTemplate.fromTemplate(`
你是一位专业的内容创作者。
请根据以下要求创作内容：

主题：{topic}
目标受众：{audience}
风格：{style}
长度：{length}

请创作高质量、原创的内容。
`);

const result = await prompt.pipe(model).invoke({
  topic: userInput.topic,
  audience: userInput.audience,
  style: userInput.style,
  length: userInput.length,
});
```

### Step 4: 内容优化

调用 `humanizer-zh` 去除 AI 味：

```bash
# 使用 humanizer-zh 优化内容
@humanizer-zh {生成的内容}
```

### Step 5: 生成输出

根据内容类型生成不同格式：

#### 公众号文章

```markdown
# [标题]

[封面图建议]

[正文内容]

---

## 金句摘录
- 金句 1
- 金句 2

## 互动话题
[引导读者互动的问题]
```

#### 视频脚本

```markdown
# 视频脚本：[标题]

## 基本信息
- 时长：约 X 分钟
- 风格：[风格]

## 脚本内容

### 开场（0:00-0:30）
[画面描述]
[旁白文案]

### 主体（0:30-X:00）
...

### 结尾（X:00-X:30）
...

## BGM 建议
- 开场：[音乐建议]
- 主体：[音乐建议]
- 结尾：[音乐建议]
```

## 内容质量标准

1. **原创性** - 不抄袭，不洗稿
2. **可读性** - 结构清晰，语言流畅
3. **价值性** - 提供有用信息或情绪价值
4. **自然性** - 去除 AI 痕迹，接近人类写作

## 与其他 Skill 协作

| 场景 | 协作方式 |
|------|----------|
| 文章配图 | 调用 `/fi-video` 生图 |
| 视频制作 | 调用 `/fi-video` 生成视频 |
| 内容发布 | 集成到项目 API |

## 输出

- Markdown 格式的内容文件
- 可选：配图建议
- 可选：SEO 元数据
