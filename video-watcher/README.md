# Video Watcher

这是我自己在本地用的一个视频 transcript skill，主要处理 YouTube 和 Bilibili。优先抓平台现成字幕，抓不到时再下载音频并调用同仓库里的 `assemblyai-transcript` 做转写。

## 这个 skill 做什么

- 支持 YouTube 和 Bilibili 视频链接
- 自动识别平台
- 优先用 `yt-dlp` 抓字幕
- 抓不到字幕时回退到音频下载 + `assemblyai-transcript`
- 中间 transcript 统一写成同一个临时 `transcript.md`
- 最终输出到 `~/Downloads`
- 脚本只负责产出 draft，后续需要 agent 读取整份 markdown 做最后整理

## 依赖

- `python3`
- `yt-dlp`
- sibling skill：`assemblyai-transcript`
- `ASSEMBLYAI_API_KEY`

## 基本流程

1. 识别是 YouTube 还是 Bilibili
2. 先用 `yt-dlp` 抓字幕
3. 如果有字幕，就清洗字幕内容并写入临时 `transcript.md`
4. 如果没有字幕，就下载音频
5. 把音频直接交给 `assemblyai-transcript`
6. `assemblyai-transcript` 返回后，再统一整理成相同的中间 markdown 格式
7. 根据视频标题把 draft markdown 输出到最终目录
8. agent 再读取最终 markdown，补摘要、轻度清洗正文、调整文段边界，并覆盖原文件

## 语言逻辑

- 默认字幕语言：
  - YouTube：`en`
  - Bilibili：`zh-CN`
- `--lang` 只影响字幕抓取偏好
- 如果进入 AssemblyAI fallback，语言检测交给 AssemblyAI 自动处理

## 中间文件格式

无论 transcript 来源于字幕还是 AssemblyAI，中间文件都统一成：

```markdown
# Intermediate Transcript

## Metadata

- Source mode: ...
- Language: ...

## Transcript

...
```

## 最终文档结构

脚本输出应被视为 draft。这个 skill 的完整 workflow 要求 agent 读取最终输出目录中的 markdown，并覆盖成统一结构：

```markdown
# <Video Title>

## 摘要

- 简洁摘要

## Metadata

- Platform: ...
- Source mode: ...
- Language: ...
- Uploader: ...
- Duration: ...
- URL: ...
- Video ID: ...

## Transcript

正文
```

注意：

- 可以整文件覆盖写回
- 但 `## Transcript` 正文只做轻度处理
- 允许修正局部明显错误
- 允许按自然边界切分文段
- 不允许把整段 transcript 改写成另一版 prose

## 用法

基础用法：

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL"
```

指定字幕偏好语言：

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL" --lang zh-CN
```

指定输出目录：

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL" --out-dir /path/to/output
```

## 适合的场景

- 想快速拿到视频 transcript
- 想先用字幕，没字幕再自动 fallback
- 想把最终文档标准化成可读的 markdown
- 想让 transcript 和 summary 工作流统一

## 相关文件

- [SKILL.md](./SKILL.md)
- [scripts/get_transcript.py](./scripts/get_transcript.py)
- [../assemblyai-transcript/README.md](../assemblyai-transcript/README.md)
