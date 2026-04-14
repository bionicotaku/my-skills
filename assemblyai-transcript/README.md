# AssemblyAI Transcript

这是我自己在本地用的一个转写 skill。它负责把本地音频文件上传到 AssemblyAI，轮询结果，然后把 transcript 保存成 markdown。

## 功能

- 输入本地音频文件
- 调用 AssemblyAI 做语音转写
- 自动轮询直到任务完成
- 默认输出到 `~/Downloads/<原音频文件名>.md`
- 支持用参数覆盖输出目录、输出文件名或完整输出路径
- 不依赖第三方 Python 包，只用标准库

## 适用场景

- 手头只有本地音频，需要快速转文字
- 需要一个 hosted speech-to-text fallback
- 想替代以前那种直接调 Whisper 上传音频的用法

## 依赖

- `python3`
- `ASSEMBLYAI_API_KEY`

## 用法

基础用法：

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a
```

指定完整输出路径：

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --save /tmp/transcript.md
```

只改输出目录：

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --out-dir /tmp
```

只改文件名：

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --name meeting-notes
```

调整轮询间隔：

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --interval 3
```

## 输出规则

- 如果传了 `--save`，就写到那个精确路径
- 如果没传 `--save`，默认写到 `~/Downloads/<原音频文件名>.md`
- `--out-dir` 用来改默认输出目录
- `--name` 用来改默认文件名
- 最终保存格式固定是 markdown

## 相关文件

- [SKILL.md](/Users/evan/Downloads/my-skills/assemblyai-transcript/SKILL.md)
- [scripts/transcribe.py](/Users/evan/Downloads/my-skills/assemblyai-transcript/scripts/transcribe.py)
