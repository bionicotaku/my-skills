# Video Watcher

Universal transcript fetcher for **YouTube** and **Bilibili** videos.

## Features

- ✅ **YouTube Support** - youtube.com, youtu.be
- ✅ **Bilibili Support** - bilibili.com, b23.tv
- ✅ **Auto Platform Detection** - Automatically identifies video platform from URL
- ✅ **Smart Subtitle Language Defaults** - zh-CN for Bilibili, en for YouTube
- ✅ **AssemblyAI Fallback** - Audio transcription is delegated to the sibling `assemblyai-transcript` skill
- ✅ **ASR Auto-Detect** - AssemblyAI fallback detects language automatically
- ✅ **Custom Subtitle Language** - Override subtitle lookup with `--lang`
- ✅ **Dual Format** - Supports both VTT and SRT subtitle formats

## Installation

### Prerequisites

Install [yt-dlp](https://github.com/yt-dlp/yt-dlp):

```bash
# macOS
brew install yt-dlp

# Linux
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod +x /usr/local/bin/yt-dlp

# Python
pip install yt-dlp
```

This skill also depends on the sibling `assemblyai-transcript` skill and its `ASSEMBLYAI_API_KEY` configuration.

### Install via ClawHub

```bash
clawhub install video-watcher
```

### Manual Installation

1. Download this skill folder
2. Place it in your OpenClaw workspace as `~/.openclaw/workspace/skills/video-watcher/`

The folder name should remain `video-watcher`, because that is the published skill name.

## Usage

### Basic Usage (Auto-detect)

```bash
# YouTube
python3 {baseDir}/scripts/get_transcript.py \
  "https://www.youtube.com/watch?v=VIDEO_ID"

# Bilibili
python3 {baseDir}/scripts/get_transcript.py \
  "https://www.bilibili.com/video/BVxxxxx"
```

### Specify Language

```bash
# Prefer English subtitles for a Bilibili video
python3 scripts/get_transcript.py "https://bilibili.com/video/..." --lang en

# Prefer Chinese subtitles for a YouTube video
python3 scripts/get_transcript.py "https://youtube.com/watch?v=..." --lang zh-CN
```

`--lang` only affects subtitle lookup. If subtitles are unavailable and the script falls back to ASR, `video-watcher` calls the sibling `assemblyai-transcript` skill and AssemblyAI detects the spoken language automatically.

The fallback downloads audio as-is and passes the resulting file directly to `assemblyai-transcript`. AssemblyAI decides whether the format is acceptable. The script does not transcode audio.

Internally, both the cleaned `yt-dlp` subtitle path and the `assemblyai-transcript` fallback path now write to the same temporary `transcript.md` file before the final markdown is generated. That intermediate file uses a consistent structure:

```markdown
# Intermediate Transcript

## Metadata

- Source mode: ...
- Language: ...

## Transcript

...
```

## Default Subtitle Languages

| Platform | Default | Common Alternatives |
|----------|---------|-------------------|
| YouTube  | `en`    | `zh-CN`, `ja`, `es`, `fr` |
| Bilibili | `zh-CN` | `en`, `zh-TW`, `ja` |

## Output Format

```markdown
# <Video Title>

## 摘要

- Concise summary bullets derived from the full document

## Metadata

- Platform: ...
- Source mode: ...
- Language: ...
- Uploader: ...
- Duration: ...
- URL: ...
- Video ID: ...

## Transcript

[Lightly cleaned transcript body with boundary-aware paragraph splits...]
```

The script output should be treated as a draft. The skill requires the agent to reopen the saved markdown in the final output directory, read the whole document, lightly clean only the transcript body, split paragraphs where needed for readability, add the summary section, and overwrite the file in the standardized structure above. Overwriting the whole file is expected; the restriction is that the `## Transcript` content should only receive light local fixes and paragraph-boundary cleanup, not a full prose rewrite.

## Troubleshooting

### "yt-dlp not found"
Install yt-dlp first (see Installation section).

### "HTTP Error 412" (Bilibili)
Your IP may be rate-limited. Solutions:
1. Use cookies: `yt-dlp --cookies-from-browser chrome "URL"`
2. Use proxy: `export HTTP_PROXY="http://proxy:port"`
3. Wait and retry

### "No subtitles found"
The video may not have subtitles available. The script will then fall back to ASR on the original downloaded audio file via `assemblyai-transcript`. If that still fails, try:
- Check if the video has CC (closed captions)
- Try different language: `--lang en` or `--lang zh-CN`
- Verify `ASSEMBLYAI_API_KEY` is configured for the `assemblyai-transcript` skill

### Final Cleanup Expectations

After the script finishes:
1. Open the saved markdown file from the final output directory.
2. Read the full document, not just the transcript section.
3. Keep the transcript content intact except for light local fixes and paragraph boundary cleanup. Rewriting the file is fine; rewriting the `## Transcript` section as a new prose version is not.
4. Add a concise summary section.
5. Overwrite the same file using the standardized structure shown above.

## License

MIT

## Credits

Adapted from [youtube-watcher](https://clawhub.ai/Michaelgathara/youtube-watcher) by Michael Gathara.
