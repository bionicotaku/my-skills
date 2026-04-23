---
name: transcript-video
description: 从 YouTube 或 Bilibili 视频中获取Speech-to-Text 转录文本。适用于你需要视频文稿来做摘要、问答或信息提取的场景。输入是视频 URL；输出 markdown 转录文件。
---

# 视频文稿提取

从 **YouTube** 和 **Bilibili** 视频中获取转录文本。

## 规则

- 脚本输出只是草稿。不要在脚本执行结束后就停止。
- 结束前始终在 agent 内完整读取保存下来的 markdown，并用最终版本覆盖回去。
- 只对 `## Transcript` 正文做轻量清理：修正明显局部错误，并在合理边界处拆分段落。不要把转录内容改写或转述成新的 prose。
- 字幕、音频和转写中间产物都只能放在临时目录里，并在最终 markdown 成功写出后删除。

## 工作流

1. 先尝试用 `yt-dlp` 获取平台字幕。
2. 如果没有字幕，就把音频下载到本地并交给同级的 `assemblyai-transcript` skill 处理。
3. 无论走哪条分支，都把中间结果写到同一个临时 `transcript.md` 路径，结构使用：`# Intermediate Transcript`、`## Metadata`、`## Transcript`。
4. 默认把 markdown 草稿保存到 `~/Downloads`，文件名取自视频标题。
5. 脚本结束后，从最终输出路径读取完整生成结果。
6. 添加简洁摘要，并且只对转录正文做一次轻量清理。
7. 用以下最终结构覆盖写回同一个 markdown 文件：
   标题
   摘要
   元数据
   转录正文
8. 清理所有中间临时文件，只保留最终 markdown 输出。

## 用法

### 自动回退获取文稿

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL"
```

### 指定语言

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL" --lang zh-CN
```

### 选择其他输出目录

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL" --out-dir /path/to/output
```

## 说明

- 支持 YouTube 和 Bilibili URL
- 依赖 `yt-dlp`
- 依赖同级 `assemblyai-transcript` skill，路径是 `../assemblyai-transcript/scripts/transcribe.py`
- 通过 `assemblyai-transcript` 这层依赖要求提供 `ASSEMBLYAI_API_KEY`
- `--lang` 用于控制字幕查找优先级；如果字幕获取失败，AssemblyAI 回退路径会自动识别语言
- 音频回退路径会把下载下来的文件直接交给 AssemblyAI，不会在本地转码
- 文件名取自视频标题，而不是附加视频 id
- 用标准化的最终结构覆盖写回同一个 markdown 文件：
  `# <Title>`
  `## 摘要`
  `## Metadata`
  `## Transcript`
- 默认输出目录：`~/Downloads`
