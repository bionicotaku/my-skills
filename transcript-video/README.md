# transcript-video

处理对 YouTube 和 Bilibili 视频链接的 transcript。优先抓平台现成字幕，抓不到时只下载音频素材，后续是否调用 `assemblyai-transcript` 由 agent 决定。

## 这个 skill 做什么

- 支持 YouTube 和 Bilibili 视频链接
- 自动识别平台
- 优先用 `yt-dlp` 抓字幕
- 抓不到字幕时回退到音频下载
- 脚本只准备素材和元数据，不直接产出最终 markdown
- 后续由 agent 决定是否调用 `assemblyai-transcript` 的单文件或 batch 入口
- 最终再由 agent 做整理、收尾和清理

## 依赖

- `python3`
- `yt-dlp`
- 如果需要 AssemblyAI fallback，后续阶段才需要 sibling skill：`assemblyai-transcript`

## 基本流程

1. 识别是 YouTube 还是 Bilibili
2. 先用 `yt-dlp` 抓字幕
3. 如果有字幕，就保存原字幕文件和清洗后的 `subtitle.txt`
4. 如果没有字幕，就只下载音频文件
5. 脚本输出 JSON，告诉 agent 这次拿到的是 `subtitle` 还是 `audio`
6. 如果是 `audio`，agent 再决定是否调用 `assemblyai-transcript/scripts/transcribe.py` 或 `transcribe_batch.py`
7. agent 生成最终 markdown，补摘要、轻度清洗正文、调整文段边界，并覆盖原文件
8. agent 最后删除这次任务的 asset 目录

## 语言逻辑

- 默认字幕语言：
  - YouTube：`en`
  - Bilibili：`zh-CN`
- `--lang` 只影响字幕抓取偏好
- 如果最后拿到的是音频素材，是否自动识别语言由后续 `assemblyai-transcript` 调用决定

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
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL"
```

指定字幕偏好语言：

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL" --lang zh-CN
```

指定 asset 工作目录：

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL" --work-dir /path/to/output
```

## 适合的场景

- 想快速拿到视频 transcript
- 想先拿到字幕/音频素材，再自己决定后续转写链路
- 想把最终文档标准化成可读的 markdown，并把清理动作放在最后一步

## 相关文件

- [SKILL.md](./SKILL.md)
- [scripts/get_transcript.py](./scripts/get_transcript.py)
- [../assemblyai-transcript/README.md](../assemblyai-transcript/README.md)
