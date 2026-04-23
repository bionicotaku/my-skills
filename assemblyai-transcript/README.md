# AssemblyAI Transcript

这是我自己在本地用的一个转写 skill。它负责把本地音频文件上传到 AssemblyAI，轮询结果，然后把 transcript 保存成 markdown。

## 功能

- 输入本地音频文件
- 调用 AssemblyAI 做语音转写
- 上传阶段输出进度、速率和 ETA
- 自动轮询直到任务完成
- 支持目录批处理，线程池并发最多 4 个文件
- 默认输出到 `~/Downloads/<原音频文件名>.md`
- 支持用参数覆盖输出目录、输出文件名或完整输出路径
- 能区分上传卡住、上传后服务端无响应、以及 transcript 仍在处理

## 适用场景

- 手头只有本地音频，需要快速转文字
- 需要一个 hosted speech-to-text fallback
- 想替代以前那种直接调 Whisper 上传音频的用法

## 依赖

- `python3`
- `httpx`
- `ASSEMBLYAI_API_KEY`

安装依赖：

```bash
pipv install -r {baseDir}/requirements.txt
```

## 用法

基础用法：

```bash
pythonv {baseDir}/scripts/transcribe.py /path/to/audio.m4a
```

指定完整输出路径：

```bash
pythonv {baseDir}/scripts/transcribe.py /path/to/audio.m4a --save /tmp/transcript.md
```

只改输出目录：

```bash
pythonv {baseDir}/scripts/transcribe.py /path/to/audio.m4a --out-dir /tmp
```

只改文件名：

```bash
pythonv {baseDir}/scripts/transcribe.py /path/to/audio.m4a --name meeting-notes
```

调整轮询间隔：

```bash
pythonv {baseDir}/scripts/transcribe.py /path/to/audio.m4a --interval 3
```

调整上传和轮询超时：

```bash
pythonv {baseDir}/scripts/transcribe.py /path/to/audio.m4a \
  --upload-write-timeout 180 \
  --upload-read-timeout 90 \
  --processing-soft-timeout 7200 \
  --hard-timeout 21600
```

批处理整个目录：

```bash
pythonv {baseDir}/scripts/transcribe_batch.py \
  --source-dir /path/to/input \
  --target-dir /path/to/output
```

批处理会沿用 `transcribe.py` 的参数，并发上限固定为 4；已有同名 markdown 会自动跳过。

## 输出规则

- 如果传了 `--save`，就写到那个精确路径
- 如果没传 `--save`，默认写到 `~/Downloads/<原音频文件名>.md`
- `--out-dir` 用来改默认输出目录
- `--name` 用来改默认文件名
- 最终保存格式固定是 markdown
- 上传阶段会输出已确认发送的字节进度
- 轮询阶段会输出当前 transcript 状态；状态长时间不变会先 warning，超过硬超时才失败

## 相关文件

- [SKILL.md](./SKILL.md)
- [requirements.txt](./requirements.txt)
- [scripts/transcribe.py](./scripts/transcribe.py)
- [scripts/transcribe_batch.py](./scripts/transcribe_batch.py)
