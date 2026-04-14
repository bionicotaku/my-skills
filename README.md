# My Skills

这是我自己的个人 skills 仓库，用来存放和维护我平时在本地使用的自定义 skill。

目前这个仓库里的内容主要偏向 transcript / video 处理，同时也补充了一些日常网页内容处理类 skill。目录保持按 skill 分组，每个 skill 自己维护 `SKILL.md`、脚本和补充文档。

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
  - [assemblyai-transcript/README.md](/Users/evan/Documents/my-skills/assemblyai-transcript/README.md)
  - [assemblyai-transcript/SKILL.md](/Users/evan/Documents/my-skills/assemblyai-transcript/SKILL.md)
  - [assemblyai-transcript/scripts/transcribe.py](/Users/evan/Documents/my-skills/assemblyai-transcript/scripts/transcribe.py)

### `img-downloader`

- 用途：从网页中提取并下载主内容图片，保持页面顺序并顺序编号保存
- 输出：默认保存到 `~/Downloads/<页面标题或自定文件夹名>/`
- 特点：临时写页面专用 extractor，必要时回退到浏览器提取，再统一调用下载脚本
- 入口：
  - [img-downloader/SKILL.md](/Users/evan/Documents/my-skills/img-downloader/SKILL.md)
  - [img-downloader/README.md](/Users/evan/Documents/my-skills/img-downloader/README.md)
  - [img-downloader/scripts/download_images.py](/Users/evan/Documents/my-skills/img-downloader/scripts/download_images.py)

### `video-watcher`

- 用途：抓取 YouTube / Bilibili 字幕；没有字幕时回退到 `assemblyai-transcript`
- 输出：脚本先生成 draft markdown，skill workflow 再要求 agent 做最后整理
- 入口：
  - [video-watcher/SKILL.md](/Users/evan/Documents/my-skills/video-watcher/SKILL.md)
  - [video-watcher/README.md](/Users/evan/Documents/my-skills/video-watcher/README.md)
  - [video-watcher/scripts/get_transcript.py](/Users/evan/Documents/my-skills/video-watcher/scripts/get_transcript.py)

## 约定

- 每个 skill 目录尽量自包含
- `SKILL.md` 负责定义 workflow 和使用规则
- `scripts/` 放实际执行脚本
- 补充说明放各自 skill 目录下的 `README.md`
