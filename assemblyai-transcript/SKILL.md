---
name: assemblyai-transcript
description: 使用 AssemblyAI 转写本地音频文件，并将结果保存为 markdown 文稿。适用于工作流需要把本地音频 transcript 的场景。输入本地音频路径；输出 markdown 文件。
metadata:
  {
    "openclaw":
      {
        "emoji": "📝",
        "requires": { "bins": ["python3"], "env": ["ASSEMBLYAI_API_KEY"] },
        "primaryEnv": "ASSEMBLYAI_API_KEY",
      },
  }
---

# AssemblyAI 音频转写

把本地音频文件上传到 AssemblyAI，创建转写任务，轮询直到完成，并将转写结果保存为本地 markdown 文件。整个流程只依赖 Python 标准库模块。

## 适用场景

在以下情况下使用这个 skill：

- 本地没有可用字幕
- 你需要为某个音频文件使用托管语音转文本服务
- 你想替代旧的 Whisper API 上传流程

## 用法

基本用法：

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a
```

保存到指定文件：

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --save /tmp/transcript.md
```

保持默认文件名规则，但改为保存到其他目录：

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --out-dir /tmp
```

仅覆盖输出文件名：

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --name meeting-notes
```

控制轮询间隔：

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --interval 3
```

## 输出行为

- 如果提供了 `--save`，就把 markdown 写到该精确路径。
- 否则默认写入 `~/Downloads/<源音频文件名>.md`。
- `--out-dir` 会覆盖默认输出目录。
- `--name` 只覆盖默认文件名，但生成文件仍然使用 `.md` 扩展名；如果你需要完全自定义路径或扩展名，请使用 `--save`。
- 保存结果是 markdown 文件，脚本仍会把进度输出到 stderr，并把便于机器读取的最终值输出到 stdout。
- 不依赖 `requests`，只使用 Python 标准库（`urllib`、`json` 等）。

## 配置

把 API key 存在 OpenClaw 的 skill 配置里，而不是系统 shell 环境变量中：

```json5
{
  skills: {
    entries: {
      "assemblyai-transcript": {
        env: {
          ASSEMBLYAI_API_KEY: "YOUR_KEY",
        },
      },
    },
  },
}
```

这样可以把密钥作用域限制在 skill 运行时，而不是暴露在全局 shell 环境中。
