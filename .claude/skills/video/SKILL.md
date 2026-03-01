---
name: video
description: 使用 Remotion 生成视频内容
trigger: /video
dependencies: []  # 可选：remotion, media-downloader 等外部工具
---

# 视频生成 Skill

使用 Remotion 生成视频内容。

## 前置条件

- 项目已初始化
- Remotion 已安装

## 执行流程

### Step 1: 确定视频类型

询问用户需要生成什么类型的视频：

1. **宣传视频** - 产品/品牌宣传
2. **教程视频** - 操作演示
3. **动画视频** - 动态图形
4. **短视频** - 抖音/快手风格

### Step 2: 收集视频需求

```
请提供以下信息：

1. 视频主题：[主题]
2. 视频时长：[秒/分钟]
3. 分辨率：[1080p / 720p / 其他]
4. 风格：[简约 / 动感 / 专业 / 其他]
5. 是否需要配音：[是/否]
6. 是否需要字幕：[是/否]
7. 素材来源：[自动搜索 / 自行提供]
```

### Step 3: 调用 Remotion Skill

```bash
# 加载 Remotion 最佳实践
@remotion-best-practices
```

### Step 4: 生成视频代码

创建 Remotion 组件：

```typescript
// client/src/videos/PromotionVideo.tsx

import { AbsoluteFill, Sequence, useVideoConfig } from 'remotion';
import { Title } from './components/Title';
import { Subtitle } from './components/Subtitle';
import { Background } from './components/Background';

export const PromotionVideo: React.FC = () => {
  const { fps, durationInFrames } = useVideoConfig();

  return (
    <AbsoluteFill>
      <Background />

      <Sequence from={0} durationInFrames={60}>
        <Title text="产品名称" />
      </Sequence>

      <Sequence from={30} durationInFrames={90}>
        <Subtitle text="产品描述文字" />
      </Sequence>

      {/* 更多序列... */}
    </AbsoluteFill>
  );
};
```

### Step 5: 配置视频参数

```typescript
// client/src/videos/config.ts

import { Composition } from 'remotion';
import { PromotionVideo } from './PromotionVideo';

export const VideoConfig = () => (
  <>
    <Composition
      id="PromotionVideo"
      component={PromotionVideo}
      durationInFrames={300}  // 10秒 @ 30fps
      fps={30}
      width={1920}
      height={1080}
    />
  </>
);
```

### Step 6: 渲染视频

```bash
# 预览视频
npx remotion preview

# 渲染输出
npx remotion render PromotionVideo out/video.mp4
```

## 视频组件库

### 标题组件

```typescript
// client/src/videos/components/Title.tsx

import { spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface TitleProps {
  text: string;
}

export const Title: React.FC<TitleProps> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    config: { damping: 100 },
  });

  return (
    <div
      style={{
        fontSize: 80,
        fontWeight: 'bold',
        transform: `scale(${scale})`,
        textAlign: 'center',
      }}
    >
      {text}
    </div>
  );
};
```

### 字幕组件

```typescript
// client/src/videos/components/Subtitle.tsx

import { interpolate, useCurrentFrame } from 'remotion';

interface SubtitleProps {
  text: string;
}

export const Subtitle: React.FC<SubtitleProps> = ({ text }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        fontSize: 40,
        opacity,
        textAlign: 'center',
        color: 'white',
      }}
    >
      {text}
    </div>
  );
};
```

## 与其他 Skill 协作

| 场景 | 协作方式 |
|------|----------|
| 视频脚本 | 先调用 `/content` 生成脚本 |
| 配音 | 调用 TTS 服务（qwen3-tts-flash） |
| 素材 | 调用生图服务（wan2.6-t2i） |

## 语音合成集成

使用阿里 DashScope TTS：

```typescript
import DashScope from 'dashscope';

async function generateVoiceover(text: string): Promise<Buffer> {
  const response = await DashScope.tts.synthesize({
    model: 'qwen3-tts-flash',
    input: text,
    voice: 'zhichu',  // 或其他音色
  });

  return response.audio;
}
```

## 输出

- MP4 视频文件
- WebM 视频文件（可选）
- 视频缩略图
- 源代码（可编辑）

## 最佳实践

1. **短小精悍** - 每个视频控制在 10-20 秒
2. **分段制作** - 长视频分段制作后拼接
3. **预览验证** - 渲染前先预览效果
4. **素材管理** - 复用组件和素材
