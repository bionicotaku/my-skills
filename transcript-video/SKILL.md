---
name: transcript-video
description: 从 YouTube 或 Bilibili 视频中提取字幕素材或下载音频素材。适用于你需要先准备视频 transcript 原始输入，再决定后续转写或整理方式的场景。输入是视频 URL；输出是字幕文本或音频文件路径与元数据。
---

# 视频文稿提取

从 **YouTube** 和 **Bilibili** 视频中获取转录文本。

## 规则

- `get_transcript.py` 只负责准备素材，不负责直接调用 `assemblyai-transcript`，也不负责产出最终 markdown。
- 如果脚本返回的是字幕素材，就直接基于字幕整理最终 markdown；不要再走 AssemblyAI。
- 如果脚本返回的是音频素材，再由 agent 根据任务上下文决定调用 `assemblyai-transcript` 的单文件脚本还是 batch 脚本，以及最终输出目录。
- YouTube / Bilibili 的 `yt-dlp` 调用如果遇到登录、验证码、风控、403、412、429 等错误，脚本会自动追加 Safari cookies 重试一次；重试仍失败就报错退出。
- 多个视频 URL 使用 `get_transcript_batch.py`，它默认用 4 进程池并发调用同一套素材准备逻辑。
- 结束前始终在 agent 内完整读取最终保存下来的 markdown，并用最终版本覆盖回去。
- 只对 `## Transcript` 正文做轻量清理：修正明显局部错误，并在合理边界处拆分段落。不要把转录内容改写或转述成新的 prose。
- 字幕、音频和其他中间产物都放在工作目录里的 asset 子目录；只有在最终 markdown 成功写出后才删除。

## 工作流

1. 先运行 `get_transcript.py`，让它尝试抓字幕；没有字幕时只下载音频。
2. 如果平台拦截触发 Safari cookies 降级，确认脚本最终成功返回；如果仍失败，不要继续猜测或伪造素材。
3. 读取脚本输出的 JSON 结果，确认本次拿到的是 `subtitle` 还是 `audio`。
4. 如果是 `subtitle`，直接基于返回的 `transcript_path` 和 `metadata.json` 生成最终 markdown。
5. 如果是 `audio`，再决定是否调用 `assemblyai-transcript/scripts/transcribe.py` 或 `assemblyai-transcript/scripts/transcribe_batch.py`，并自己决定输出目录。
6. 拿到最终 transcript 后，补简洁摘要，并且只对转录正文做一次轻量清理。
7. 用以下最终结构覆盖写回最终 markdown：
   标题
   摘要
   元数据
   转录正文
8. 最终 markdown 成功写出后，删除这次任务对应的 asset 目录。

## 用法

### 准备视频素材

```bash
python {baseDir}/scripts/get_transcript.py "VIDEO_URL"
```

### 指定语言

```bash
python {baseDir}/scripts/get_transcript.py "VIDEO_URL" --lang zh-CN
```

### 指定 asset 工作目录

```bash
python {baseDir}/scripts/get_transcript.py "VIDEO_URL" --work-dir /path/to/workdir
```

### 批量准备视频素材

```bash
python {baseDir}/scripts/get_transcript_batch.py --input-file urls.txt
```

## 说明

- 支持 YouTube 和 Bilibili URL
- 依赖 `yt-dlp`
- `get_transcript.py` 的 stdout 是结构化 JSON，至少会给出 `kind`、`asset_dir`、`metadata_path` 和素材路径
- `--lang` 只用于控制字幕查找优先级；如果最后返回的是音频素材，后续是否自动识别语言由 `assemblyai-transcript` 决定
- Safari cookies 只作为 `yt-dlp` 失败后的降级路径，不是默认路径；Bilibili 原有 `User-Agent` 和 `Referer` header 会继续保留
- `get_transcript_batch.py` 默认 `--workers 4`，输出 JSON 汇总；任意 URL 失败时最终退出码为 1
- asset 目录名来自视频标题和视频 id，方便后续 agent 明确清理范围
- 最终 markdown 仍然要由 agent 用标准化结构覆盖写回：
  `# <Title>`
  `## 摘要`
  `## Metadata`
  `## Transcript`
- 默认 asset 工作目录：`~/Downloads/transcript-video-assets`
