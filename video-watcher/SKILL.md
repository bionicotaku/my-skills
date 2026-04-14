---
name: video-watcher
description: Fetch a transcript from a YouTube or Bilibili video and save it as markdown. Use when you need a video transcript for summarization, question answering, or information extraction. Input is a video URL; output is a markdown transcript file in `~/Downloads` by default, which this skill treats as a draft for final cleanup and formatting.
---

# Video Watcher

Fetch transcripts from **YouTube** and **Bilibili** videos.

## Rules

- The script output is only a draft. Do not stop after script execution.
- Before finishing, always read the full saved markdown in-agent and overwrite it with the finalized version.
- Only do light cleanup on the `## Transcript` body: fix obvious local errors and split paragraphs at sensible boundaries. Do not rewrite or paraphrase the transcript as new prose.
- Keep subtitle, audio, and transcription intermediates inside a temporary directory only, and delete them after the final markdown is successfully written.

## Workflow

1. Try to fetch platform subtitles with `yt-dlp`.
2. If subtitles are unavailable, download audio locally and pass it to the sibling `assemblyai-transcript` skill.
3. In either branch, write the intermediate result to the same temporary `transcript.md` path using this structure: `# Intermediate Transcript`, `## Metadata`, `## Transcript`.
4. Save a draft markdown transcript to `~/Downloads` by default, naming the file from the video title.
5. After the script finishes, read the entire generated markdown from the final output path.
6. Add a concise summary and do a light cleanup pass on the transcript body only.
7. Overwrite the same markdown file with this final structure:
   title
   summary
   metadata
   transcript body
8. Clean up all intermediate temporary files and keep only the final markdown output.

## Usage

### Get transcript with automatic fallback

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL"
```

### Specify language

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL" --lang zh-CN
```

### Choose a different output folder

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL" --out-dir /path/to/output
```

## Notes

- Support YouTube and Bilibili URLs
- Require `yt-dlp`
- Require the sibling `assemblyai-transcript` skill at `../assemblyai-transcript/scripts/transcribe.py`
- Require `ASSEMBLYAI_API_KEY` through the `assemblyai-transcript` dependency
- `--lang` controls subtitle lookup preference; if subtitle fetch fails, the AssemblyAI fallback detects language automatically
- The audio fallback passes the downloaded file directly to AssemblyAI and does not transcode it locally
- Name files from the video title instead of appending the video id
- Overwrite the same markdown file with the standardized final structure:
  `# <Title>`
  `## 摘要`
  `## Metadata`
  `## Transcript`
- Default output directory: `~/Downloads`
