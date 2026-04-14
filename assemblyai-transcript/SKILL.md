---
name: assemblyai-transcript
description: Upload local audio files to AssemblyAI for transcription, poll until completion, and save the transcript markdown to `~/Downloads` by default using the source audio filename unless the output path, directory, or name is overridden. Use when a workflow needs a hosted speech-to-text fallback to replace OpenAI Whisper API style audio upload transcription, without any extra Python package dependencies.
metadata:
  {
    "openclaw": {
      "emoji": "📝",
      "requires": { "bins": ["python3"], "env": ["ASSEMBLYAI_API_KEY"] },
      "primaryEnv": "ASSEMBLYAI_API_KEY"
    }
  }
---

# AssemblyAI Transcript

Upload a local audio file to AssemblyAI, create a transcript job, poll until completion, and save transcript markdown locally using only Python standard library modules.

## When to use

Use this skill when:
- local subtitles are unavailable
- you need hosted speech-to-text for an audio file
- you want a replacement for the old Whisper API upload flow

## Usage

Basic:

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a
```

Save to a specific file:

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --save /tmp/transcript.md
```

Save to a different folder while keeping the default filename behavior:

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --out-dir /tmp
```

Override just the output name:

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --name meeting-notes
```

Control polling interval:

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --interval 3
```

## Output behavior

- If `--save` is provided, writes markdown to that exact path.
- Otherwise writes to `~/Downloads/<source-audio-filename>.md`.
- `--out-dir` overrides the default output directory.
- `--name` overrides the default filename, but the generated file still uses `.md`; use `--save` if you need a fully custom path or extension.
- The saved file is markdown and the script still prints progress to stderr and machine-useful final values to stdout.
- No `requests` dependency, only Python stdlib (`urllib`, `json`, etc.).

## Configuration

Store the API key in OpenClaw skill config, not a system shell variable:

```json5
{
  skills: {
    entries: {
      "assemblyai-transcript": {
        env: {
          ASSEMBLYAI_API_KEY: "YOUR_KEY"
        }
      }
    }
  }
}
```

This keeps the key scoped to the skill runtime instead of your global shell environment.
