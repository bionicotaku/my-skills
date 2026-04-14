---
name: video-watcher
description: Fetch transcripts from YouTube and Bilibili videos. Use when you need to summarize a video, answer questions about its content, or extract information from it. Prefer this skill for transcript work because it first fetches subtitles with yt-dlp and, when subtitles are unavailable, automatically downloads audio locally and delegates transcription to the sibling `assemblyai-transcript` skill, then saves a markdown draft in the system Downloads folder. The draft is never the final deliverable: the assistant must always read the full markdown, manually clean the result in-agent, split paragraphs for readability, add a concise summary, and overwrite the file with the standardized final version.
---

# Video Watcher

Fetch transcripts from **YouTube** and **Bilibili** videos.

Critical requirement:
- The script output is only a draft. Before finishing, the agent must always manually read and clean the full generated markdown in-agent, then write back the finalized version. Do not stop after script execution or draft generation.

Workflow:
1. Try to fetch platform subtitles with `yt-dlp`
2. If no subtitles are available, download audio locally
3. Whether the transcript came from cleaned `yt-dlp` subtitles or the AssemblyAI fallback, write it first to the same temporary `transcript.md` path using the same intermediate markdown structure: `# Intermediate Transcript`, `## Metadata`, and `## Transcript`
4. If subtitles are unavailable, pass the downloaded audio file directly to the sibling `assemblyai-transcript` skill, which writes to that same temporary `transcript.md` path using AssemblyAI language detection
5. Save a draft markdown transcript in the system `~/Downloads` folder by default
6. Name the markdown file from the video title
7. After the script finishes, read the entire generated markdown from the final output path and review it in-agent
8. Do a light cleanup pass on the transcript body only: fix obvious local errors and split paragraphs at sensible boundaries. You may overwrite the entire markdown file when saving, but do not perform a wholesale rewrite, paraphrase, or full reorganization of the `## Transcript` content itself
9. Write a concise summary section based on the full document
10. Overwrite the markdown with the standardized final structure:
   title
   summary
   metadata
   transcript body
11. Keep all intermediate subtitle/audio/transcription files inside a temporary directory only
12. After the final markdown is successfully written, manually clean up all intermediate temporary files and keep only the final markdown output

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
- Both subtitle and AssemblyAI branches normalize their intermediate output to the same temporary `transcript.md` markdown file with the same `# Intermediate Transcript` / `## Metadata` / `## Transcript` structure before final formatting
- The audio fallback passes the downloaded file directly to AssemblyAI and does not transcode it locally
- The script output is only a draft; the agent must perform the final cleanup and summary pass on the saved markdown file
- Name files from the video title instead of appending the video id
- After script generation, read the entire markdown file and do a human-style in-agent polish pass
- Only do light transcript-body cleanup and boundary-aware paragraph splitting. It is fine to rewrite the whole markdown file as a file operation, but do not rewrite the `## Transcript` section as prose
- Overwrite the same markdown file with the standardized final structure:
  `# <Title>`
  `## 摘要`
  `## Metadata`
  `## Transcript`
- Store subtitle/audio/transcription intermediates only in a temporary folder, then delete them after success so no residual process files remain
- Default output directory: `~/Downloads`
