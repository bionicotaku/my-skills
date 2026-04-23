# transcript-video

处理对 YouTube 和 Bilibili 视频链接的 transcript。优先抓平台现成字幕，抓不到时只下载音频素材，后续是否调用 `assemblyai-transcript` 由 agent 决定。

## 这个 skill 做什么

- 支持 YouTube 和 Bilibili 视频链接
- 自动识别平台
- 优先用 `yt-dlp` 抓字幕
- 抓不到字幕时回退到音频下载
- YouTube / Bilibili 遇到登录、验证码、风控、403、412、429 等 `yt-dlp` 错误时，会用 Safari cookies 自动重试一次
- 脚本只准备素材和元数据，不直接产出最终 markdown
- 只有下载音频素材时会把 `yt-dlp` 进度输出到 stderr；stdout 始终保留为最终 JSON
- 后续由 agent 决定是否调用 `assemblyai-transcript` 的单文件或 batch 入口
- 最终再由 agent 做整理、收尾和清理
- 批量入口使用 4 进程池并发处理多个 URL，仍然只准备素材

## 依赖

- `python`
- `yt-dlp`
- 如果需要 AssemblyAI fallback，后续阶段才需要 sibling skill：`assemblyai-transcript`

## 基本流程

1. 识别是 YouTube 还是 Bilibili
2. 先用 `yt-dlp` 抓字幕
3. 如果有字幕，就保存原字幕文件和清洗后的 `subtitle.txt`
4. 如果没有字幕，就只下载音频文件
5. 如果字幕或音频阶段被平台登录/风控拦截，脚本会保留原命令参数并追加 `--cookies-from-browser safari` 重试一次
6. 如果 Safari cookies 重试仍失败，脚本直接报错退出，并输出首次错误和 Safari cookies 错误
7. 脚本输出 JSON，告诉 agent 这次拿到的是 `subtitle` 还是 `audio`
8. 如果是 `audio`，agent 再决定是否调用 `assemblyai-transcript/scripts/transcribe.py` 或 `transcribe_batch.py`
9. agent 生成最终 markdown，补摘要、轻度清洗正文、调整文段边界，并覆盖原文件
10. agent 最后删除这次任务的 asset 目录

## 语言逻辑

- 默认字幕语言：
  - YouTube：`en`
  - Bilibili：`zh-CN`
- `--lang` 只影响字幕抓取偏好
- 如果最后拿到的是音频素材，是否自动识别语言由后续 `assemblyai-transcript` 调用决定

## Safari cookies 降级

- 默认不读取浏览器 cookies，只有 `yt-dlp` 返回登录、验证码、风控、403、412、429 等疑似认证/反爬错误时才重试。
- 重试使用 `--cookies-from-browser safari`，适用于 YouTube 和 Bilibili。
- Bilibili 的 `User-Agent` 和 `Referer` header 会继续保留，Safari cookies 只是追加参数。
- 如果 Safari cookies 因 macOS 权限、未登录、cookies 失效或平台继续拦截而失败，脚本会停止，不再静默回退。

## 命令行输出

- stdout 只输出最终 JSON，方便 agent 或脚本继续解析。
- metadata 阶段保持安静。
- 字幕阶段会在 stderr 打印 `Download type: subtitles (<lang>)`，但不显示详细进度。
- 下载音频素材阶段会显示 `yt-dlp` 原生进度到 stderr，便于观察下载速度、百分比和剩余时间。

## 素材目录结构

每次运行会在工作目录里创建一个基于标题和视频 id 的 asset 子目录，例如：

```text
<work-dir>/
  <title>-<video-id>/
    metadata.json
    subtitle.vtt|subtitle.srt
    subtitle.txt
    audio.<ext>
```

其中：

- 有字幕时会保存 `subtitle.vtt|subtitle.srt` 和清洗后的 `subtitle.txt`
- 无字幕时会保存下载下来的 `audio.<ext>`
- `metadata.json` 始终存在，供后续整理最终 markdown 使用

## 用法

基础用法：

```bash
python {baseDir}/scripts/get_transcript.py "VIDEO_URL"
```

指定字幕偏好语言：

```bash
python {baseDir}/scripts/get_transcript.py "VIDEO_URL" --lang zh-CN
```

指定 asset 工作目录：

```bash
python {baseDir}/scripts/get_transcript.py "VIDEO_URL" --work-dir /path/to/output
```

批量处理多个 URL：

```bash
python {baseDir}/scripts/get_transcript_batch.py "VIDEO_URL_1" "VIDEO_URL_2"
```

从文件批量处理：

```bash
python {baseDir}/scripts/get_transcript_batch.py --input-file urls.txt
```

批量脚本默认使用 4 个 worker 进程。它会尽量跑完所有 URL，stdout 输出 JSON 汇总；只要有任意 URL 失败，脚本最终退出码就是 1。

## 适合的场景

- 想快速拿到视频 transcript
- 想先拿到字幕/音频素材，再自己决定后续转写链路
- 想把最终文档标准化成可读的 markdown，并把清理动作放在最后一步

## 相关文件

- [SKILL.md](./SKILL.md)
- [scripts/get_transcript.py](./scripts/get_transcript.py)
- [scripts/get_transcript_batch.py](./scripts/get_transcript_batch.py)
- [../assemblyai-transcript/README.md](../assemblyai-transcript/README.md)
