---
name: assemblyai-transcript
description: 使用 AssemblyAI 转写本地音频文件，并将结果保存为 markdown 文稿。适用于工作流需要把本地音频 transcript 的场景。输入本地音频路径；输出 markdown 文件。
---

# AssemblyAI 音频转写

把本地音频文件上传到 AssemblyAI，创建转写任务，轮询直到完成，并将转写结果保存为本地 markdown 文件。也提供目录批处理入口，线程池并发最多 4 个文件。上传阶段会输出进度，轮询阶段会区分状态仍在推进还是请求已超时。

## 适用场景

在以下情况下使用这个 skill：

- 你需要为某个音频文件使用托管语音转文本服务

## 用法

基本用法：

```bash
python {baseDir}/scripts/transcribe.py /path/to/audio.m4a
```

保存到指定文件：

```bash
python {baseDir}/scripts/transcribe.py /path/to/audio.m4a --save /tmp/transcript.md
```

保持默认文件名规则，但改为保存到其他目录：

```bash
python {baseDir}/scripts/transcribe.py /path/to/audio.m4a --out-dir /tmp
```

仅覆盖输出文件名：

```bash
python {baseDir}/scripts/transcribe.py /path/to/audio.m4a --name meeting-notes
```

控制轮询间隔：

```bash
python {baseDir}/scripts/transcribe.py /path/to/audio.m4a --interval 3
```

批处理整个目录：

```bash
python {baseDir}/scripts/transcribe_batch.py --source-dir /path/to/input --target-dir /path/to/output
```

先安装依赖：

```bash
pip install -r {baseDir}/requirements.txt
```

## 输出行为

- 如果提供了 `--save`，就把 markdown 写到该精确路径。
- 否则默认写入 `~/Downloads/<源音频文件名>.md`。
- `--out-dir` 会覆盖默认输出目录。
- `--name` 只覆盖默认文件名，但生成文件仍然使用 `.md` 扩展名；如果你需要完全自定义路径或扩展名，请使用 `--save`。
- 保存结果是 markdown 文件，脚本仍会把进度输出到 stderr，并把便于机器读取的最终值输出到 stdout。
- 依赖 `httpx` 做分块上传和分阶段超时控制。
- batch 模式会对目录下支持的媒体文件做非递归扫描，并发最多 4 个；目标目录里已有同名 `.md` 时会跳过。

## 运行约束

- 大文件上传和长音频处理都可能持续很久。
- 只要脚本进程还在运行，或者 stderr/stdout 还在持续输出上传进度、状态日志、warning，就不要让 agent 自己判断“应该已经超时了”并提前中断。
- 只有在脚本明确退出报错，或者脚本自己命中了 `hard timeout` 并返回失败时，才把这次任务视为真正超时。
- 如果只是长时间停在 `processing`，但脚本还在按轮询间隔继续输出状态，这表示服务端仍在处理，不是 agent 应该手动打断的场景。
