# My Skills

这是我自己的本地 skills 仓库，用来集中维护日常使用的自定义 skill。

目前仓库里的内容主要分成两类：
- transcript / video / 网页内容处理
- agent workflow / memory / 仓库同步

每个 skill 尽量按目录自包含，通常包含：
- `SKILL.md`：技能定义、触发条件、工作流
- `README.md`：更详细的使用说明
- `scripts/`：实际执行脚本
- 其他辅助文档：按 skill 自己的需要保留

## 目录

```text
my-skills/
├── README.md
├── .gitignore
├── assemblyai-transcript/
│   ├── README.md
│   ├── SKILL.md
│   └── scripts/
│       └── transcribe.py
├── img-downloader/
│   ├── README.md
│   ├── SKILL.md
│   └── scripts/
│       └── download_images.py
├── self-improving/
│   ├── README.md
│   ├── SKILL.md
│   ├── boundaries.md
│   ├── heartbeat-rules.md
│   ├── setup.md
│   ├── hooks/
│   │   └── openclaw/
│   │       ├── HOOK.md
│   │       ├── handler.js
│   │       └── handler.ts
│   └── references/
│       └── examples.md
├── skill-repo-sync/
│   ├── README.md
│   ├── SKILL.md
│   └── scripts/
│       └── sync_skills.py
└── video-watcher/
    ├── README.md
    ├── SKILL.md
    └── scripts/
        └── get_transcript.py
```

## 当前 Skills

### `assemblyai-transcript`

- 用途：把本地音频上传到 AssemblyAI 做转写
- 输出：默认保存到 `~/Downloads/<原音频名>.md`
- 入口：
  - [assemblyai-transcript/README.md](./assemblyai-transcript/README.md)
  - [assemblyai-transcript/SKILL.md](./assemblyai-transcript/SKILL.md)
  - [assemblyai-transcript/scripts/transcribe.py](./assemblyai-transcript/scripts/transcribe.py)

### `img-downloader`

- 用途：从网页中提取并下载主内容图片，保持页面顺序并顺序编号保存
- 输出：默认保存到 `~/Downloads/<页面标题或自定文件夹名>/`
- 特点：临时写页面专用 extractor，必要时回退到浏览器提取，再统一调用下载脚本
- 入口：
  - [img-downloader/README.md](./img-downloader/README.md)
  - [img-downloader/SKILL.md](./img-downloader/SKILL.md)
  - [img-downloader/scripts/download_images.py](./img-downloader/scripts/download_images.py)

### `self-improving`

- 用途：canonical OpenClaw self-improvement workflow
- 核心模型：
  - raw layer：`~/.openclaw/workspace/.learnings/`
  - promoted layer：`~/self-improving/`
- 作用：
  - 把失败、首次经验、知识缺口、能力缺口先记录到 raw layer
  - 把确认后的长期规则、偏好、domain/project 模式提升到 promoted layer
  - 用保守 heartbeat 维护 promoted memory
- 特点：
  - 明确区分 raw capture 和 long-term memory
  - promotion 保守、显式、可审计
  - 只保留最小 OpenClaw-native hook，不再维护 repo-level hook 杂项
- 入口：
  - [self-improving/README.md](./self-improving/README.md)
  - [self-improving/SKILL.md](./self-improving/SKILL.md)
  - [self-improving/setup.md](./self-improving/setup.md)
  - [self-improving/heartbeat-rules.md](./self-improving/heartbeat-rules.md)

### `skill-repo-sync`

- 用途：把一个源 skills 目录中的 skill 同步到另一个目标 skills 目录
- 同步策略：同名 skill 覆盖更新，缺失 skill 自动复制，目标目录中其他 skill 保持不变
- 特点：调用时显式传入源目录和目标目录的绝对路径，不再依赖脚本位置推导源目录
- 入口：
  - [skill-repo-sync/README.md](./skill-repo-sync/README.md)
  - [skill-repo-sync/SKILL.md](./skill-repo-sync/SKILL.md)
  - [skill-repo-sync/scripts/sync_skills.py](./skill-repo-sync/scripts/sync_skills.py)

### `video-watcher`

- 用途：抓取 YouTube / Bilibili 字幕；没有字幕时回退到 `assemblyai-transcript`
- 输出：脚本先生成 draft markdown，skill workflow 再要求 agent 做最后整理
- 入口：
  - [video-watcher/README.md](./video-watcher/README.md)
  - [video-watcher/SKILL.md](./video-watcher/SKILL.md)
  - [video-watcher/scripts/get_transcript.py](./video-watcher/scripts/get_transcript.py)

## 仓库约定

- 每个 skill 目录尽量自包含
- `SKILL.md` 负责定义 workflow 和使用规则
- `README.md` 负责补充更详细的背景、说明和示例
- `scripts/` 放实际执行脚本
- 只有在确实有价值时，才额外保留 `references/`、`hooks/`、`assets/` 之类辅助目录

## 当前维护方向

- transcript / video skill 继续偏实用工作流
- `self-improving` 作为 canonical memory / learning skill 持续收敛
- 避免在仓库里保留已经退役但语义重叠的旧 skill
- 优先保持每个 skill 结构清晰、职责单一、引用自洽
